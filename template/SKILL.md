---
name: your-skill-name
description: One or two sentences on what the skill does and the outcome it produces. Use when the user asks to ..., mentions ..., or is working on ...
---

# Skill Title

One-line statement of the goal and the quality bar.

## 1. Gather context
- What to read or run before acting (files, commands, questions to ask the user).

## 2. Do the work
- Numbered, imperative steps. Prefer concrete commands and examples over prose.
- Put long reference material in `references/` and deterministic helpers in `scripts/`.

## 3. Verify
- How to prove the result is correct (tests, linters, a command and its expected output).

## 4. Report
```markdown
<The exact output format the user should receive.>
```

## Guardrails
- What the agent must never do without explicit user approval.
