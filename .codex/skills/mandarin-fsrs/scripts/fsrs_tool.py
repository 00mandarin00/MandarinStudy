from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Iterable

from fsrs import Card, Rating, Scheduler


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parents[2]
DEFAULT_DB_PATH = REPO_ROOT / "study_data" / "mandarin-fsrs.sqlite3"

DATE_FMT = "%Y-%m-%d"
RATING_MAP = {
    "again": Rating.Again,
    "hard": Rating.Hard,
    "good": Rating.Good,
    "easy": Rating.Easy,
}
LEVEL_TO_RATING_STEPS = {
    0: ["again"],
    1: ["hard"],
    2: ["good", "good"],
    3: ["good", "good", "easy"],
}
LEVEL_TO_STATUS = {
    0: "active",
    1: "active",
    2: "active",
    3: "maintenance",
}


@dataclass
class MatrixRow:
    item: str
    item_type: str
    level: int
    status: str
    last_reviewed: str
    next_review: str
    next_action: str


def now_utc() -> datetime:
    return datetime.now(UTC)


def strip_ticks(value: str) -> str:
    return value.strip().replace("`", "")


def today_str() -> str:
    return now_utc().date().isoformat()


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def iso_at_start_of_day(date_text: str) -> str:
    return datetime.strptime(date_text, DATE_FMT).replace(tzinfo=UTC).isoformat()


def iso_to_date_text(value: str | None) -> str:
    if not value:
        return ""
    if "T" in value:
        return value.split("T", 1)[0]
    return value


def parse_date_or_default(value: str | None, *, default: str | None = None) -> str:
    if value:
        datetime.strptime(value, DATE_FMT)
        return value
    if default is not None:
        return default
    return today_str()


def connect_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_key TEXT NOT NULL UNIQUE,
            note_file TEXT NOT NULL,
            review_file TEXT,
            item_text TEXT NOT NULL,
            item_type TEXT NOT NULL,
            prompt TEXT,
            answer TEXT,
            level INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'active',
            last_reviewed TEXT,
            next_review TEXT,
            next_action TEXT,
            card_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            reviewed_at TEXT NOT NULL,
            rating TEXT NOT NULL,
            due_before TEXT,
            due_after TEXT,
            review_log_json TEXT,
            FOREIGN KEY (item_id) REFERENCES items(id)
        );

        CREATE INDEX IF NOT EXISTS idx_items_next_review ON items(next_review);
        CREATE INDEX IF NOT EXISTS idx_items_note_file ON items(note_file);
        CREATE INDEX IF NOT EXISTS idx_reviews_item_id ON reviews(item_id);
        """
    )
    conn.commit()


def load_scheduler() -> Scheduler:
    return Scheduler()


def card_to_json(card: Card) -> str:
    if hasattr(card, "to_json"):
        return card.to_json()
    return json.dumps(card.to_dict())  # pragma: no cover


def card_from_json(payload: str) -> Card:
    if hasattr(Card, "from_json"):
        return Card.from_json(payload)
    return Card.from_dict(json.loads(payload))  # pragma: no cover


def review_log_to_json(review_log: object) -> str:
    if hasattr(review_log, "to_json"):
        return review_log.to_json()
    if hasattr(review_log, "to_dict"):
        return json.dumps(review_log.to_dict())
    return json.dumps({"repr": repr(review_log)})


def note_file_from_review_file(review_file: Path) -> Path:
    basename = review_file.name
    if not basename.endswith(".review.md"):
        raise ValueError(f"Expected a .review.md file, got {review_file}")
    note_name = basename.replace(".review.md", ".md")
    return review_file.parent.parent / note_name


def infer_item_key(note_file: Path, item_text: str) -> str:
    return f"{note_file.name}::{item_text}"


def parse_matrix(review_file: Path) -> list[MatrixRow]:
    lines = review_file.read_text(encoding="utf-8").splitlines()
    header = "| Item | Type | Level | Status | Last Reviewed | Next Review | Next Action |"
    legacy_header = "| Item | Type | Level | Last Reviewed | Next Action |"

    for index, line in enumerate(lines):
        if line.strip() == header:
            rows_start = index + 2
            return parse_matrix_rows(lines[rows_start:], has_status=True)
        if line.strip() == legacy_header:
            rows_start = index + 2
            return parse_matrix_rows(lines[rows_start:], has_status=False)

    raise ValueError(f"No mastery matrix found in {review_file}")


def parse_matrix_rows(lines: Iterable[str], *, has_status: bool) -> list[MatrixRow]:
    rows: list[MatrixRow] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line.startswith("|"):
            break
        parts = [part.strip() for part in line.strip("|").split("|")]
        if has_status:
            if len(parts) != 7:
                continue
            item, item_type, level, status, last_reviewed, next_review, next_action = parts
        else:
            if len(parts) != 5:
                continue
            item, item_type, level, last_reviewed, next_action = parts
            status = LEVEL_TO_STATUS.get(int(level), "active")
            next_review = last_reviewed
        rows.append(
            MatrixRow(
                item=strip_ticks(item),
                item_type=strip_ticks(item_type),
                level=int(level),
                status=status,
                last_reviewed=last_reviewed,
                next_review=next_review,
                next_action=strip_ticks(next_action),
            )
        )
    return rows


def seed_card(level: int, reviewed_at: datetime) -> Card:
    scheduler = load_scheduler()
    card = Card()
    reviewed_at = ensure_utc(reviewed_at)
    steps = LEVEL_TO_RATING_STEPS.get(level, ["again"])
    step_count = len(steps)
    for offset, rating_name in enumerate(steps, start=step_count):
        review_time = reviewed_at - timedelta(days=offset)
        review_result = scheduler.review_card(card, RATING_MAP[rating_name], review_time)
        if isinstance(review_result, tuple):
            card = review_result[0]
        elif isinstance(review_result, dict):
            card = review_result[RATING_MAP[rating_name]][0]
        else:
            raise TypeError("Unexpected review result from fsrs Scheduler.review_card")
    return card


def extract_review_result(result: object, rating: Rating) -> tuple[Card, object]:
    if isinstance(result, tuple) and len(result) == 2:
        return result[0], result[1]
    if isinstance(result, dict):
        card, review_log = result[rating]
        return card, review_log
    raise TypeError("Unexpected review result from fsrs Scheduler.review_card")


def import_matrix(args: argparse.Namespace) -> None:
    review_file = Path(args.review_file).resolve()
    note_file = Path(args.note_file).resolve() if args.note_file else note_file_from_review_file(review_file)
    rows = parse_matrix(review_file)
    db_path = Path(args.db).resolve()

    conn = connect_db(db_path)
    init_db(conn)

    now_text = now_utc().isoformat()
    inserted = 0
    updated = 0

    for row in rows:
        last_reviewed = parse_date_or_default(row.last_reviewed)
        next_review = parse_date_or_default(row.next_review, default=last_reviewed)
        reviewed_at = datetime.strptime(last_reviewed, DATE_FMT).replace(tzinfo=UTC)
        next_review_iso = iso_at_start_of_day(next_review)
        item_key = infer_item_key(note_file, row.item)
        existing = conn.execute("SELECT id FROM items WHERE item_key = ?", (item_key,)).fetchone()
        card = seed_card(row.level, reviewed_at)
        if existing:
            conn.execute(
                """
                UPDATE items
                SET note_file = ?, review_file = ?, item_text = ?, item_type = ?, prompt = ?, answer = ?,
                    level = ?, status = ?, last_reviewed = ?, next_review = ?, next_action = ?,
                    card_json = ?, updated_at = ?
                WHERE item_key = ?
                """,
                (
                    str(note_file),
                    str(review_file),
                    row.item,
                    row.item_type,
                    row.item,
                    "",
                    row.level,
                    row.status,
                    last_reviewed,
                    next_review_iso,
                    row.next_action,
                    card_to_json(card),
                    now_text,
                    item_key,
                ),
            )
            updated += 1
        else:
            conn.execute(
                """
                INSERT INTO items (
                    item_key, note_file, review_file, item_text, item_type, prompt, answer,
                    level, status, last_reviewed, next_review, next_action, card_json,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item_key,
                    str(note_file),
                    str(review_file),
                    row.item,
                    row.item_type,
                    row.item,
                    "",
                    row.level,
                    row.status,
                    last_reviewed,
                    next_review_iso,
                    row.next_action,
                    card_to_json(card),
                    now_text,
                    now_text,
                ),
            )
            inserted += 1

    conn.commit()
    print(f"Imported {inserted} items, updated {updated} items from {review_file}")


def due_items(args: argparse.Namespace) -> None:
    db_path = Path(args.db).resolve()
    conn = connect_db(db_path)
    init_db(conn)

    due_date = parse_date_or_default(args.on)
    cutoff = (
        datetime.strptime(due_date, DATE_FMT).replace(tzinfo=UTC) + timedelta(days=1) - timedelta(microseconds=1)
    ).isoformat()
    params: list[object] = [cutoff]
    query = """
        SELECT item_key, note_file, item_text, item_type, level, status, next_review, next_action
        FROM items
        WHERE next_review IS NOT NULL AND next_review <= ?
    """
    if args.note_file:
        query += " AND note_file = ?"
        params.append(str(Path(args.note_file).resolve()))
    query += " ORDER BY next_review ASC, level ASC, item_text ASC"
    if args.limit:
        query += " LIMIT ?"
        params.append(args.limit)

    rows = conn.execute(query, tuple(params)).fetchall()
    for row in rows:
        print(
            json.dumps(
                {
                    "item_key": row["item_key"],
                    "note_file": row["note_file"],
                    "item": row["item_text"],
                    "type": row["item_type"],
                    "level": row["level"],
                    "status": row["status"],
                    "next_review": row["next_review"],
                    "next_action": row["next_action"],
                },
                ensure_ascii=True,
            )
        )
    if not rows:
        print("No due items.")


def adjusted_level(old_level: int, rating_name: str) -> int:
    if rating_name == "again":
        return max(0, old_level - 1)
    if rating_name == "hard":
        return max(0, old_level)
    if rating_name == "good":
        return min(3, old_level + 1)
    return 3


def next_status(level: int) -> str:
    return "maintenance" if level >= 3 else "active"


def next_action_for_rating(item_text: str, rating_name: str) -> str:
    if rating_name == "again":
        return f"relearn {item_text}"
    if rating_name == "hard":
        return f"review {item_text} with hint support"
    if rating_name == "good":
        return f"standard recall check for {item_text}"
    return f"light maintenance check for {item_text}"


def review_item(args: argparse.Namespace) -> None:
    db_path = Path(args.db).resolve()
    conn = connect_db(db_path)
    init_db(conn)

    row = conn.execute(
        """
        SELECT id, item_key, item_text, level, status, card_json, next_review
        FROM items
        WHERE item_key = ?
        """,
        (args.item_key,),
    ).fetchone()
    if row is None:
        raise SystemExit(f"Unknown item key: {args.item_key}")

    rating_name = args.rating.lower()
    rating = RATING_MAP[rating_name]
    scheduler = load_scheduler()
    reviewed_at = now_utc()
    old_card = card_from_json(row["card_json"])
    result = scheduler.review_card(old_card, rating, reviewed_at)
    new_card, review_log = extract_review_result(result, rating)

    due_after_dt = getattr(new_card, "due", None)
    if isinstance(due_after_dt, datetime):
        due_after = ensure_utc(due_after_dt).isoformat()
    elif due_after_dt is not None:
        due_after = str(due_after_dt)
    else:
        due_after = reviewed_at.isoformat()

    new_level = adjusted_level(row["level"], rating_name)
    new_status = next_status(new_level)
    next_action = next_action_for_rating(row["item_text"], rating_name)
    reviewed_iso = reviewed_at.date().isoformat()

    conn.execute(
        """
        UPDATE items
        SET level = ?, status = ?, last_reviewed = ?, next_review = ?, next_action = ?,
            card_json = ?, updated_at = ?
        WHERE id = ?
        """,
        (
            new_level,
            new_status,
            reviewed_iso,
            due_after,
            next_action,
            card_to_json(new_card),
            reviewed_at.isoformat(),
            row["id"],
        ),
    )
    conn.execute(
        """
        INSERT INTO reviews (item_id, reviewed_at, rating, due_before, due_after, review_log_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            row["id"],
            reviewed_at.isoformat(),
            rating_name,
            row["next_review"],
            due_after,
            review_log_to_json(review_log),
        ),
    )
    conn.commit()

    print(
        json.dumps(
            {
                "item_key": row["item_key"],
                "item": row["item_text"],
                "rating": rating_name,
                "level": new_level,
                "status": new_status,
                "next_review": due_after,
                "next_action": next_action,
            },
            ensure_ascii=True,
        )
    )


def sync_matrix(args: argparse.Namespace) -> None:
    review_file = Path(args.review_file).resolve()
    db_path = Path(args.db).resolve()
    conn = connect_db(db_path)
    init_db(conn)

    db_rows = conn.execute(
        """
        SELECT item_text, item_type, level, status, last_reviewed, next_review, next_action
        FROM items
        WHERE review_file = ?
        ORDER BY item_text ASC
        """,
        (str(review_file),),
    ).fetchall()
    if not db_rows:
        raise SystemExit(f"No items found for {review_file}")

    lines = review_file.read_text(encoding="utf-8").splitlines()
    header = "| Item | Type | Level | Status | Last Reviewed | Next Review | Next Action |"
    separator = "| --- | --- | --- | --- | --- | --- | --- |"
    new_block = [header, separator]
    for row in db_rows:
        new_block.append(
            "| `{}` | {} | {} | {} | {} | {} | {} |".format(
                row["item_text"],
                row["item_type"],
                row["level"],
                row["status"],
                row["last_reviewed"] or "",
                iso_to_date_text(row["next_review"]),
                row["next_action"] or "",
            )
        )

    start = None
    end = None
    for index, line in enumerate(lines):
        if line.strip() == "## Mastery Matrix":
            start = index + 1
            continue
        if start is not None and index > start and line.startswith("## "):
            end = index
            break

    if start is None:
        raise SystemExit(f"Could not find '## Mastery Matrix' in {review_file}")
    if end is None:
        end = len(lines)

    updated_lines = lines[:start] + [""] + new_block + [""] + lines[end:]
    review_file.write_text("\n".join(updated_lines).rstrip() + "\n", encoding="utf-8")
    print(f"Synchronized mastery matrix in {review_file}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage Mandarin FSRS study items.")
    parser.add_argument("--db", default=str(DEFAULT_DB_PATH), help="SQLite database path")

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init-db", help="Initialize the SQLite database")
    init_parser.set_defaults(func=lambda args: init_db(connect_db(Path(args.db).resolve())))

    import_parser = subparsers.add_parser("import-matrix", help="Import mastery matrix rows into SQLite")
    import_parser.add_argument("--review-file", required=True, help="Path to the review-history markdown file")
    import_parser.add_argument("--note-file", help="Path to the source note markdown file")
    import_parser.set_defaults(func=import_matrix)

    due_parser = subparsers.add_parser("due", help="List due items")
    due_parser.add_argument("--note-file", help="Filter by note file")
    due_parser.add_argument("--on", help="Due date in YYYY-MM-DD format; defaults to today")
    due_parser.add_argument("--limit", type=int, help="Maximum number of results")
    due_parser.set_defaults(func=due_items)

    review_parser = subparsers.add_parser("review", help="Record a review result and reschedule")
    review_parser.add_argument("--item-key", required=True, help="Stable item key, e.g. 20260312.md::mei qu guo")
    review_parser.add_argument(
        "--rating",
        required=True,
        choices=sorted(RATING_MAP.keys()),
        help="Review result quality",
    )
    review_parser.set_defaults(func=review_item)

    sync_parser = subparsers.add_parser("sync-matrix", help="Write DB-backed matrix values back to markdown")
    sync_parser.add_argument("--review-file", required=True, help="Path to the review-history markdown file")
    sync_parser.set_defaults(func=sync_matrix)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
