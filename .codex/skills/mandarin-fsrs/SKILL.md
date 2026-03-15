---
name: mandarin-fsrs
description: Use when the user wants FSRS-based spaced repetition for Mandarin notes, wants to schedule or reschedule review items with SQLite, or wants to sync a review-history mastery matrix into an FSRS-backed study queue.
---

# Mandarin FSRS

Use this skill when the user wants real spaced-repetition scheduling instead of only handwritten review notes.

## What this skill does

- keeps durable study-item state in SQLite
- uses `py-fsrs` for scheduling after each rating
- imports items from a review-history `Mastery Matrix`
- lists due items for review sessions
- records ratings like `again`, `hard`, `good`, and `easy`

## Files

- Project config: `pyproject.toml`
- Wrapper: `scripts/fsrs_run.sh`
- Script: `scripts/fsrs_tool.py`
- Default database: `study_data/mandarin-fsrs.sqlite3`

## Workflow

1. Start from a note and its review-history file.
2. Run the wrapper instead of raw `uv run`. It pins `uv` to the system `python3` and writable `/tmp` locations for cache and the project environment:
   - `bash ./scripts/fsrs_run.sh --help`
3. If needed, import the note's matrix into SQLite:
   - `bash ./scripts/fsrs_run.sh import-matrix --review-file /abs/path/review_history/20260312.review.md`
4. List due items:
   - `bash ./scripts/fsrs_run.sh due`
   - optionally filter with `--note-file /abs/path/20260312.md`
5. During review, record the user result:
   - `bash ./scripts/fsrs_run.sh review --item-key "20260312.md::mei qu guo" --rating good`
6. If useful, sync the latest DB state back into the matrix:
   - `bash ./scripts/fsrs_run.sh sync-matrix --review-file /abs/path/review_history/20260312.review.md`

## Environment notes

- Prefer `scripts/fsrs_run.sh` for all normal operations. It avoids three common sandbox issues:
  - unwritable `uv` cache under `$HOME/.cache/uv`
  - unwritable uv-managed Python directories under `$HOME/.local/share/uv`
  - unwritable project `.venv` creation inside the skill directory
- The wrapper sets:
  - `UV_CACHE_DIR=/tmp/uv-cache`
  - `UV_PROJECT_ENVIRONMENT=/tmp/mandarin-fsrs-venv`
  - `UV_NO_MANAGED_PYTHON=1`
  - `UV_PYTHON=python3`
- For a due-only check, it is acceptable to query `study_data/mandarin-fsrs.sqlite3` directly with `sqlite3` or stdlib `sqlite3` if `uv` still cannot run. That fallback is only for reading due state, not for scheduling reviews.

## Rating guide

- `again` = did not remember, major miss
- `hard` = remembered with strain or needed help
- `good` = correct with normal effort
- `easy` = immediate and confident

## Seeding policy

When importing an existing mastery matrix, seed cards from the current level rather than pretending to know the full historical timeline.

- `Level 0-1` -> weak seed
- `Level 2` -> moderate seed
- `Level 3` -> strong seed

This keeps the starting schedule reasonable, and real reviews quickly override the seed.

## Notes

- Keep the Markdown review history as the human-readable study log.
- Treat SQLite as the scheduling engine.
- If the matrix and database disagree, prefer the database for due scheduling and use `sync-matrix` to refresh the Markdown file.
