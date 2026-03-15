# Project Instructions

## Skills
A skill is a set of local instructions to follow that is stored in a `SKILL.md` file. Below is the list of skills that can be used in this project.

### Available skills
- mandarin-class-review: Use when the user wants to review a Mandarin class-notes file interactively, practice vocabulary or grammar from a note, or update lightweight progress notes for future review sessions. (file: /home/zero/Projects/MandarinStudy/.codex/skills/mandarin-class-review/SKILL.md)

### How to use skills
- Discovery: The list above is the skills available in this project for this session.
- Trigger rules: If the user names a skill or clearly asks for note review, vocabulary review, grammar review, lesson prep, or progress-note updates, use the matching skill.
- Missing/blocked: If a listed skill cannot be read, say so briefly and continue with the best fallback.
- How to use a skill:
  1. Open its `SKILL.md`.
  2. Read only enough to follow the workflow.
  3. Load only the specific note files or progress files needed for the current review session.
- Context hygiene:
  - Keep context tight.
  - Prefer opening the requested note file and, if present, its matching review-history file.
