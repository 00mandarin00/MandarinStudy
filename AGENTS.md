# Project Instructions

## Skills
A skill is a set of local instructions to follow that is stored in a `SKILL.md` file. Below is the list of skills that can be used in this project.

### Available skills
- mandarin-class-review: Use when the user wants to review a Mandarin class-notes file interactively, practice vocabulary or grammar from a note, or update lightweight progress notes for future review sessions. (file: /home/zero/Projects/MandarinStudy/.codex/skills/mandarin-class-review/SKILL.md)
- mandarin-fsrs: Use when the user wants FSRS-based spaced repetition for Mandarin notes, wants to schedule review items with SQLite, or wants to sync a mastery matrix into a database-backed study queue. (file: /home/zero/Projects/MandarinStudy/.codex/skills/mandarin-fsrs/SKILL.md)
- mandarin-note-cleanup: Use when the user wants rough pinyin-only Mandarin class lines cleaned into structured lesson notes with grouped topics, identified grammar patterns, and added English glosses, while keeping all Chinese in pinyin and excluding Hanzi. (file: /home/zero/Projects/MandarinStudy/.codex/skills/mandarin-note-cleanup/SKILL.md)

### How to use skills
- Discovery: The list above is the skills available in this project for this session.
- Trigger rules: If the user names a skill or clearly asks for note review, vocabulary review, grammar review, lesson prep, progress-note updates, or cleanup of rough pinyin class notes into structured study notes, use the matching skill.
- Missing/blocked: If a listed skill cannot be read, say so briefly and continue with the best fallback.
- How to use a skill:
  1. Open its `SKILL.md`.
  2. Read only enough to follow the workflow.
  3. Load only the specific note files or progress files needed for the current review session.
- Context hygiene:
  - Keep context tight.
  - Prefer opening the requested note file and, if present, its matching review-history file.
