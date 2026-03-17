---
name: mandarin-class-review
description: Use when the user wants interactive review of a Mandarin class-notes file, especially before a lesson. This skill runs review mostly in English, keeps all Chinese in pinyin unless the user explicitly asks otherwise, and can maintain lightweight per-class progress notes about what the user got right, wrong, or found difficult.
---

# Mandarin Class Review

Use this skill when the user wants to review a Mandarin note file, practice vocabulary or grammar from it, or continue a prior review session for the same note.

If the user wants spaced-repetition scheduling, due queues, or SQLite-backed review state, also use `mandarin-fsrs`.

## When to use it

- interactive lesson prep
- vocabulary review from a note
- grammar review from a note
- lightweight review-history updates for a specific lesson

## When not to use it

- cleaning messy notes into structured study notes; use `mandarin-note-cleanup`
- FSRS scheduling or durable spaced-repetition state; use `mandarin-fsrs`
- broad repo-management tasks unless the user explicitly asks for them

## Default behavior

- Converse primarily in English.
- Keep all Chinese in pinyin unless the user explicitly asks for Hanzi or tones.
- Keep the session interactive. Do not dump the entire note back to the user unless asked.
- Review in short turns: one word, one phrase, one contrast, or one grammar pattern at a time.
- Match the user's pace. Give hints before answers when the user seems unsure.
- Correct mistakes clearly without pretending uncertain notes are correct.

## Default workflow

1. Read the requested note file.
2. If present and relevant, read the matching file in `review_history/`.
3. Build a review inventory from the note before prompting:
   - vocabulary
   - grammar patterns
   - example sentences
   - easy-to-confuse pairs
4. Start an interactive review loop using a small study set from that inventory.
5. Recycle missed items later in the session.
6. At the end, summarize what looked strong and what still needs work.
7. Only update `review_history/` if the user wants progress saved.

## Optional branches

If the user wants progress saved:

- store notes in `review_history/<note-basename>.review.md`
- keep the file short and practical
- include:
  - session date
  - strong items
  - shaky items
  - items to revisit next time

If the user wants a mastery matrix:

- initialize it from the full note inventory, not just the prompts used in one session
- add missing note items on later passes
- update only the rows touched or clearly implied by the session
- leave untouched rows in place so coverage gaps stay visible

If the user wants git syncing:

- treat `git pull`, `git commit`, and `git push` as explicit opt-in actions
- if any git step fails, report the error briefly and stop for user guidance

If the user wants FSRS-based review:

- use `mandarin-fsrs` to import or sync the matrix
- choose due items first when practical
- record graded outcomes through the FSRS workflow

## Review style

- Mix recognition and recall:
  - English to pinyin
  - pinyin to English
  - explain a grammar pattern
  - fill in a missing word
  - correct a slightly wrong sentence
- Prioritize material that is:
  - new in the note
  - easy to confuse
  - important for conversation
  - unreviewed
  - previously shaky

## Difficulty control

- Start slightly easier unless the user asks for a harder drill.
- If the user misses an item, revisit it later in the same session.
- If the user answers quickly and correctly, move on.
- Every few turns, briefly summarize what seems stable versus shaky.

## Review-history format

Store progress in `review_history/<note-basename>.review.md`.

Example:

- `20260312.md` -> `review_history/20260312.review.md`

Suggested minimal format:

```md
# Review History for 20260312

## 2026-03-15
- Strong: `guo` vs `le` in basic examples
- Shaky: `ba` sentence structure
- Revisit: `bang mang` vs `bang zhu`, `ziji`, `yibian ... yibian ...`
```

If the user wants a mastery matrix, use a compact table like:

```md
## Mastery Matrix

| Item | Type | Level | Status | Last Reviewed | Next Review | Next Action |
| --- | --- | --- | --- | --- | --- | --- |
| `Bei Fang` | vocab | 0 | unreviewed |  | 2026-03-15 | introduce meaning and region contrast |
| `guo` vs `le` | grammar | 2 | active | 2026-03-15 | 2026-03-22 | contrast experience vs completed action |
```

Use these meanings:

- `Level 0` = new or not remembered
- `Level 1` = partial recall
- `Level 2` = mostly correct
- `Level 3` = fast and reliable
- `unreviewed` = in the note inventory but not yet tested live
- `active` = should be reviewed regularly
- `maintenance` = stable enough for lighter follow-up

## File guidance

- Read only the note file the user asked for.
- If the note is long, build a useful subset instead of reviewing top to bottom.
- Preserve the user's romanization unless a correction is clearly helpful.
- If a note seems inconsistent or mistaken, raise it during review instead of silently rewriting the source.

## Minimal examples

- "Review `/abs/path/20260312.md` with me."
- "Quiz me on grammar from this lesson."
- "Use the review history too, but do not save anything yet."
- "Save a short review summary after we finish."
