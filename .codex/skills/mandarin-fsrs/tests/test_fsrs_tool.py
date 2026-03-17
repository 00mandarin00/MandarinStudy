from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import sqlite3
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path
from unittest import mock


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "fsrs_tool.py"
SPEC = importlib.util.spec_from_file_location("fsrs_tool", SCRIPT_PATH)
fsrs_tool = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = fsrs_tool
SPEC.loader.exec_module(fsrs_tool)


class FSRSToolTests(unittest.TestCase):
    def test_new_card_good_and_hard_can_repeat_same_local_day(self) -> None:
        scheduler = fsrs_tool.load_scheduler()
        reviewed_at = datetime(2026, 3, 16, 21, 0, tzinfo=fsrs_tool.STUDY_TZ).astimezone(UTC)

        good_result = scheduler.review_card(fsrs_tool.Card(), fsrs_tool.Rating.Good, reviewed_at)
        hard_result = scheduler.review_card(fsrs_tool.Card(), fsrs_tool.Rating.Hard, reviewed_at)

        good_card, _ = fsrs_tool.extract_review_result(good_result, fsrs_tool.Rating.Good)
        hard_card, _ = fsrs_tool.extract_review_result(hard_result, fsrs_tool.Rating.Hard)

        self.assertEqual(good_card.due.astimezone(fsrs_tool.STUDY_TZ).date().isoformat(), "2026-03-16")
        self.assertEqual(hard_card.due.astimezone(fsrs_tool.STUDY_TZ).date().isoformat(), "2026-03-16")

    def test_due_uses_study_timezone_cutoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "fsrs.sqlite3"
            conn = fsrs_tool.connect_db(db_path)
            fsrs_tool.init_db(conn)
            conn.execute(
                """
                INSERT INTO items (
                    item_key, note_file, review_file, item_text, item_type, prompt, answer,
                    level, status, last_reviewed, next_review, next_action, card_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "note.md::late-item",
                    "/tmp/note.md",
                    "/tmp/review.md",
                    "late-item",
                    "vocab",
                    "late-item",
                    "",
                    0,
                    "active",
                    "2026-03-15",
                    "2026-03-17T03:14:23+00:00",
                    "review late-item with hint support",
                    fsrs_tool.card_to_json(fsrs_tool.Card()),
                    "2026-03-15T00:00:00+00:00",
                    "2026-03-15T00:00:00+00:00",
                ),
            )
            conn.commit()

            args = argparse.Namespace(db=str(db_path), on="2026-03-16", note_file=None, limit=None)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                fsrs_tool.due_items(args)

            due_rows = [json.loads(line) for line in output.getvalue().splitlines() if line.strip()]
            self.assertEqual([row["item_key"] for row in due_rows], ["note.md::late-item"])

    def test_review_item_stamps_last_reviewed_in_study_timezone(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "fsrs.sqlite3"
            conn = fsrs_tool.connect_db(db_path)
            fsrs_tool.init_db(conn)
            now_text = "2026-03-15T00:00:00+00:00"
            conn.execute(
                """
                INSERT INTO items (
                    item_key, note_file, review_file, item_text, item_type, prompt, answer,
                    level, status, last_reviewed, next_review, next_action, card_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "note.md::hello",
                    "/tmp/note.md",
                    "/tmp/review.md",
                    "hello",
                    "vocab",
                    "hello",
                    "",
                    0,
                    "active",
                    "2026-03-15",
                    "2026-03-16T00:00:00+00:00",
                    "introduce hello",
                    fsrs_tool.card_to_json(fsrs_tool.Card()),
                    now_text,
                    now_text,
                ),
            )
            conn.commit()

            review_args = argparse.Namespace(db=str(db_path), item_key="note.md::hello", rating="good")
            fake_now = datetime(2026, 3, 17, 3, 5, tzinfo=UTC)
            with mock.patch.object(fsrs_tool, "now_utc", return_value=fake_now):
                with contextlib.redirect_stdout(io.StringIO()):
                    fsrs_tool.review_item(review_args)

            row = sqlite3.connect(db_path).execute(
                "SELECT last_reviewed FROM items WHERE item_key = ?",
                ("note.md::hello",),
            ).fetchone()
            self.assertEqual(row[0], "2026-03-16")


if __name__ == "__main__":
    unittest.main()
