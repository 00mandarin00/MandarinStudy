---
name: mandarin-note-cleanup
description: Use when the user wants rough pinyin-only Mandarin class lines cleaned into structured lesson notes with grouped topics, identified grammar patterns, and added English glosses, while keeping all Chinese in pinyin and excluding Hanzi.
---

# Mandarin Note Cleanup

Use this skill when the user has messy or partial class notes in pinyin and wants them rewritten into clean study notes similar to the project's lesson-note files.

If the user wants interactive drilling or progress tracking after cleanup, also use `mandarin-class-review`. If the user wants spaced repetition scheduling or SQLite-backed review queues, also use `mandarin-fsrs`.

## Core behavior

- Keep all Chinese in pinyin only.
- Do not add Hanzi unless the user explicitly asks for it.
- Add concise English meanings or translations throughout.
- Group related material into clear topical sections instead of preserving raw line order.
- Identify grammar patterns taught in the lesson and separate them from simple vocabulary when possible.
- Preserve the user's underlying meaning, but smooth wording, casing, and formatting for readability.
- If a raw line is ambiguous or likely mistaken, mark it gently instead of pretending certainty.

## Default output shape

Prefer a cleaned lesson note that looks like the existing class files in this repo:

1. Topic headings such as `# Family`, `# Cleaning`, or `# Food / Kitchen`
2. Short pattern sections such as `# Grammar` or `# Guo/Le`
3. For grammar-heavy items:
   - a one-line meaning or usage note
   - a `## Structure` block when a reusable pattern exists
   - a `## Examples` block with pinyin plus English
4. For vocabulary-heavy items:
   - `term: English`
   - optionally short example lines when they clarify usage

## Workflow

1. Read only the note file or pasted text the user wants cleaned.
2. Scan for:
   - repeated themes or semantic clusters
   - explicit grammar patterns
   - example sentences
   - possible transcription mistakes or unclear fragments
3. Reorganize the content into a small number of useful sections:
   - region or culture
   - vocabulary themes
   - grammar patterns
   - example sentences
   Adjust section names to fit the lesson instead of forcing a fixed taxonomy.
4. Add English glosses to every retained item.
5. Normalize formatting:
   - title case or sentence case headings
   - one item per line
   - consistent colon usage for vocabulary entries
   - blank lines between sections
6. Keep pinyin readable as written by the user unless a correction is clearly needed.
7. If you correct likely pinyin or wording issues, note the assumption briefly in the response.

## Grammar identification guidance

When sorting the lesson, pull out patterns such as:

- tense/aspect markers like `le`, `guo`, `zhe`
- disposal or word-order patterns like `ba`
- comparison or evaluation patterns
- paired structures like `yibian ... yibian ...`
- resultative or directional complements when they appear

When a pattern is present, create a dedicated section for it rather than burying it inside a vocab list.

## Cleanup style

- Prefer short, practical English.
- Keep examples conversational and faithful to the original note.
- Do not over-explain grammar unless the user asks for more detail.
- Do not invent extra vocabulary just to fill a section.
- If a line could belong in more than one section, place it where it is most useful for later study.

## File-editing guidance

When the user wants the note file updated:

- edit only the requested file
- preserve unrelated content that is already well structured
- replace rough note blocks with cleaned sections instead of appending duplicate material

When the user only wants help drafting or previewing cleanup:

- provide the cleaned version in chat first
- ask before overwriting the source file if that was not explicit

## Boundaries

- This skill is for organizing and clarifying notes, not for claiming uncertain Mandarin is definitely correct.
- If the source text is too fragmentary to interpret safely, say which lines are unclear and offer the best structured draft from what is recoverable.
