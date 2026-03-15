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
- Script: `scripts/fsrs_tool.py`
- Default database: `study_data/mandarin-fsrs.sqlite3`

## Workflow

1. Start from a note and its review-history file.
2. If needed, import the note's matrix into SQLite:
   - `uv run scripts/fsrs_tool.py import-matrix --review-file /abs/path/review_history/20260312.review.md`
3. List due items:
   - `uv run scripts/fsrs_tool.py due`
   - optionally filter with `--note-file /abs/path/20260312.md`
4. During review, record the user result:
   - `uv run scripts/fsrs_tool.py review --item-key "20260312.md::mei qu guo" --rating good`
5. If useful, sync the latest DB state back into the matrix:
   - `uv run scripts/fsrs_tool.py sync-matrix --review-file /abs/path/review_history/20260312.review.md`

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
