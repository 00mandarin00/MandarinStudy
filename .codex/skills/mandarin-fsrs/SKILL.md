---
name: mandarin-fsrs
description: Use when the user wants FSRS-based spaced repetition for Mandarin notes, wants to schedule or reschedule review items with SQLite, or wants to sync a review-history mastery matrix into an FSRS-backed study queue.
---

# Mandarin FSRS

Use this skill when the user wants real spaced-repetition scheduling rather than only handwritten review notes.

## When to use it

- import a lesson matrix into SQLite
- list due items
- record review ratings such as `again`, `hard`, `good`, or `easy`
- sync scheduling state back into a markdown review file

## When not to use it

- interactive note cleanup without scheduling
- ordinary lesson drilling when the user does not want spaced repetition

## Source of truth

- SQLite is the source of truth for scheduling state.
- Markdown review-history files are the human-readable log.
- If the database and markdown disagree, prefer the database for scheduling and use `sync-matrix` to refresh markdown.

## Files

- project config: `.codex/skills/mandarin-fsrs/pyproject.toml`
- wrapper: `.codex/skills/mandarin-fsrs/scripts/fsrs_run.sh`
- script: `.codex/skills/mandarin-fsrs/scripts/fsrs_tool.py`
- default database: `study_data/mandarin-fsrs.sqlite3`

## Default workflow

1. Start from a note and, if present, its review-history file.
2. Use the wrapper instead of raw `uv run`:
   - `bash ./.codex/skills/mandarin-fsrs/scripts/fsrs_run.sh --help`
3. If needed, import the markdown matrix into SQLite:
   - `bash ./.codex/skills/mandarin-fsrs/scripts/fsrs_run.sh import-matrix --review-file /abs/path/review_history/20260312.review.md`
4. List due items:
   - `bash ./.codex/skills/mandarin-fsrs/scripts/fsrs_run.sh due`
   - optionally filter with `--note-file /abs/path/20260312.md`
5. During review, record the user result:
   - `bash ./.codex/skills/mandarin-fsrs/scripts/fsrs_run.sh review --item-key "20260312.md::mei qu guo" --rating good`
6. If the user wants markdown updated, sync the latest database state back:
   - `bash ./.codex/skills/mandarin-fsrs/scripts/fsrs_run.sh sync-matrix --review-file /abs/path/review_history/20260312.review.md`

## Environment notes

Prefer `.codex/skills/mandarin-fsrs/scripts/fsrs_run.sh` for normal operations. It avoids common sandbox and writability problems by setting:

- `UV_CACHE_DIR=/tmp/uv-cache`
- `UV_PROJECT_ENVIRONMENT=/tmp/mandarin-fsrs-venv`
- `UV_NO_MANAGED_PYTHON=1`
- `UV_PYTHON=python3`

For a due-only check, it is acceptable to read `study_data/mandarin-fsrs.sqlite3` directly with `sqlite3` or stdlib `sqlite3` if the wrapper cannot run. Use that only for read-only inspection, not for scheduling updates.

Canonical SQLite fallback for due-only checks:

```sh
sqlite3 -header -column study_data/mandarin-fsrs.sqlite3 \
  "SELECT item_key, item_text, item_type, level, status, date(next_review) AS due_date
   FROM items
   WHERE next_review IS NOT NULL AND date(next_review) <= date('now')
   ORDER BY note_file, datetime(next_review), id;"
```

## Rating guide

- `again` = major miss
- `hard` = remembered with strain or help
- `good` = correct with normal effort
- `easy` = immediate and confident

## Seeding policy

When importing an existing mastery matrix, seed from the current level instead of pretending to know the full review history.

- `Level 0-1` -> weak seed
- `Level 2` -> moderate seed
- `Level 3` -> strong seed

Real reviews should override the initial seed quickly.

## Coordination with other skills

- Use with `mandarin-class-review` when the user wants due-item-driven drilling.
- Use with `mandarin-note-cleanup` only after the note content is stable enough to schedule.

## Minimal examples

- "Import this lesson's matrix into FSRS."
- "Show due items for `/abs/path/20260312.md`."
- "Record this item as `hard`."
- "Sync the DB state back into the review markdown."
