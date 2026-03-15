---
name: mandarin-class-review
description: Use when the user wants interactive review of a Mandarin class-notes file, especially before a lesson. This skill runs review mostly in English, keeps all Chinese in pinyin unless the user explicitly asks otherwise, and can maintain lightweight per-class progress notes about what the user got right, wrong, or found difficult.
---

# Mandarin Class Review

Use this skill when the user wants to review one of their Mandarin note files, practice vocabulary or grammar from it, or maintain session-to-session study notes.

## Core behavior

- Converse primarily in English.
- Use pinyin for Chinese terms and examples. Do not switch to Hanzi unless the user explicitly asks for it.
- Keep the session interactive. Do not dump the whole file back at the user unless they ask.
- Prefer short review turns: one word, one pattern, or one grammar point at a time.
- Match the user's pacing. If they seem unsure, slow down and give hints before giving the answer.
- Be encouraging, but correct mistakes clearly.

## Workflow

1. Start by syncing the repository with `git pull` so the review session includes any notes saved from another device.
2. Read the target class-notes file.
3. If it exists, also read the matching review-history file in `review_history/`.
4. Extract a small study set from the notes:
   - vocabulary
   - grammar patterns
   - example sentences
   - likely confusion pairs or near-duplicates
5. Start an interactive review loop.
6. At the end, offer to update the matching review-history file with concise notes.
7. If session results were saved, run `git commit -am "<clear summary>"` and `git push` so the updated review history stays in sync across devices.

If `git pull`, `git commit`, or `git push` fails, explain the error briefly and stop for user guidance instead of guessing through a merge or conflict.

## Review style

- Default to prompts like:
  - "Let's review this word."
  - "What does this pattern mean?"
  - "How would you say this in pinyin?"
  - "What is the difference between these two forms?"
- Mix recognition and recall:
  - English -> pinyin
  - pinyin -> English
  - explain the grammar pattern
  - fill in one missing word
  - correct a slightly wrong sentence
- Prefer material that is:
  - new in the note
  - easy to confuse
  - important for conversation

## Difficulty control

- Start with easier recall unless the user asks for a harder drill.
- If the user misses something, recycle it later in the same session.
- If the user gets something right quickly, move on instead of over-drilling.
- Every few turns, briefly summarize patterns the user seems to know well versus patterns that still need work.

## Review-history files

Store progress notes in `review_history/<note-basename>.review.md`.

Example:
- `20260312.md` -> `review_history/20260312.review.md`

Keep these files short and practical. Include:
- session date
- what was strong
- what was shaky
- words or patterns to revisit next time
- optionally, a lightweight mastery matrix for targeted review planning

Suggested format:

```md
# Review History for 20260312

## 2026-03-15
- Strong: `guo` vs `le` in basic examples
- Shaky: `ba` sentence structure
- Revisit: `bang mang` vs `bang zhu`, `ziji`, `yibian ... yibian ...`
```

If ongoing review planning would benefit from more structure, add a compact mastery matrix near the top of the review-history file and update only the rows touched in the session.

Suggested matrix:

```md
## Mastery Matrix

| Item | Type | Level | Last Reviewed | Next Action |
| --- | --- | --- | --- | --- |
| `guo` vs `le` | grammar | 2 | 2026-03-15 | contrast experience vs completed action |
| `yibian ... yibian ...` | grammar | 3 | 2026-03-15 | occasional mixed recall |
| `zhaogu` vs `zhao dao` | vocab pair | 2 | 2026-03-15 | test meaning both directions |
| `luan fang` | phrase | 1 | 2026-03-15 | practice word order |
```

Level guide:
- `0` = new or not remembered
- `1` = partial recall, frequent mistakes
- `2` = mostly correct, occasional slips
- `3` = fast and reliable

Use the matrix to choose prompts efficiently:
- prioritize `0-1` items first
- mix in a few `2` items for reinforcement
- touch `3` items only briefly unless they start slipping

Only create or update the review-history file if the user wants the notes saved, or if the user previously asked to keep ongoing progress notes for this note set.

When saving session results, include the updated review-history file in the git commit. Use a concise message such as `Update review history for 20260312`.

## File-reading guidance

- Read only the specific note file requested by the user.
- If the file is long, build a review set first instead of covering everything in order.
- Preserve the user's romanization as written unless a correction is helpful.
- If the notes appear inconsistent, ask during review rather than silently rewriting the source material.

## Boundaries

- This skill is for guided review, not for pretending uncertain notes are correct.
- If a note likely contains an error, flag it gently and explain the best interpretation in English with pinyin examples.
- If the user asks for Hanzi, tones, or a more immersive Chinese-only mode, follow that explicit request for the current session.
