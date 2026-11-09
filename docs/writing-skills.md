# Writing a great skill

A skill is a folder containing `SKILL.md` and optional `scripts/`, `references/` and `assets/`. The agent sees only the frontmatter `description` until a task matches; then it reads the whole file.

## Anatomy

```
plugins/<plugin>/skills/<skill-name>/
├── SKILL.md            # required
├── scripts/            # deterministic helpers (prefer Python stdlib or POSIX shell)
├── references/         # long reference material loaded only when needed
└── assets/             # templates, sample files
```

```yaml
---
name: skill-name            # lowercase-hyphen, matches the folder, ≤ 64 chars
description: What it does and the outcome. Use when the user asks to ..., mentions ..., or ...
---
```

## The description is the trigger
The agent decides whether to load your skill **from the description alone**. Make it:
- **Specific about outcomes:** "Writes Conventional Commits messages from the staged diff", not "Helps with git".
- **Rich in trigger phrases** users actually say: "commit", "commit message", "squash", "clean up history".
- **Explicit about when:** end with `Use when ...`.
- ≤ 1024 characters, no angle brackets.

## The body is a playbook
1. **Gather context first.** What to read, run or ask before acting.
2. **Numbered, imperative steps.** Concrete commands and examples beat prose.
3. **Verification.** How the agent proves the result (tests, linters, measurements).
4. **Output format.** Show the exact report or artifact shape.
5. **Guardrails.** What requires explicit user approval (force push, deleting data, rewriting history).

## Quality bar
- Under 500 lines. Move deep reference material to `references/` and link to it.
- Every command in the skill has been run at least once.
- No vendor lock-in where avoidable: show the common alternatives.
- Scripts: no third-party dependencies, `--help`, meaningful exit codes, tests in `tests/`.
- Test fixtures containing fake secrets are built at runtime (string concatenation), never as literal tokens.

## Checklist before opening a PR
- [ ] `python3 scripts/validate.py` passes
- [ ] `python3 -m unittest discover tests` passes
- [ ] Skill added to the catalog table in `README.md` and the badge count updated
- [ ] Entry added under `[Unreleased]` in `CHANGELOG.md`
