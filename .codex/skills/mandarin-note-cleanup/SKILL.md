---
name: mandarin-note-cleanup
description: Use when the user wants rough pinyin-only Mandarin class lines cleaned into structured lesson notes with grouped topics, identified grammar patterns, and added English glosses, while keeping all Chinese in pinyin and excluding Hanzi.
---

# Mandarin Note Cleanup

Use this skill when the user has messy or partial pinyin notes and wants them rewritten into cleaner study notes that fit this repo's lesson style.

If the user wants interactive review after cleanup, also use `mandarin-class-review`. If the user wants spaced repetition or SQLite-backed review queues, also use `mandarin-fsrs`.

## When to use it

- clean rough class notes
- reorganize a lesson into clearer study sections
- separate grammar patterns from vocabulary
- add concise English glosses to pinyin notes

## When not to use it

- interactive drilling without note cleanup
- FSRS scheduling
- broad rewriting of already-clean files unless the user asked for it

## Default behavior

- Keep all Chinese in pinyin only unless the user explicitly asks for Hanzi.
- Add concise English meanings throughout.
- Group related material into useful sections instead of preserving raw line order.
- Separate reusable grammar patterns from plain vocabulary when possible.
- Preserve the user's meaning while smoothing formatting, casing, and organization.
- If a line is ambiguous or likely mistaken, mark the uncertainty instead of pretending certainty.

## Default workflow

1. Read only the note file or pasted text the user wants cleaned.
2. Identify:
   - repeated themes
   - grammar patterns
   - example sentences
   - likely transcription errors
3. Reorganize into a small number of useful sections.
4. Add English glosses to every retained item.
5. Normalize formatting for readability.
6. If a correction seems necessary, note the assumption briefly in the response.

## Canonical output shape

Prefer a compact lesson note with sections like:

1. topical headings such as `# Family`, `# Food`, or `# Cleaning`
2. a grammar section when the lesson teaches reusable patterns
3. vocabulary entries in `term: English` form
4. examples in pinyin plus English when they clarify usage

Use a structure like:

```md
# Topic

item: English
item: English

# Grammar

pattern: short meaning

## Structure

pattern template

## Examples

- pinyin sentence: English
- pinyin sentence: English
```

Adjust section names to fit the lesson rather than forcing a fixed taxonomy.

## Grammar identification guidance

Pull out patterns such as:

- `le`, `guo`, `zhe`
- `ba`
- comparisons
- paired structures like `yibian ... yibian ...`
- resultative or directional complements

When a reusable pattern is present, give it its own section instead of burying it in a vocabulary list.

## File-editing guidance

When the user explicitly wants the file updated:

- edit only the requested file
- preserve unrelated content that is already clear
- replace rough blocks rather than appending duplicate cleaned sections

When the user only wants a draft or preview:

- provide the cleaned note first
- do not overwrite the source unless the user asked for that

## Boundaries

- Do not claim uncertain Mandarin is definitely correct.
- Do not invent vocabulary to fill out sections.
- If the source is too fragmentary, say which lines are unclear and produce the best structured draft from what is recoverable.

## Minimal examples

- "Clean up this pasted lesson."
- "Turn `/abs/path/20260312.md` into a structured note."
- "Separate grammar from vocab but keep everything in pinyin."
- "Preview the cleaned version before editing the file."
