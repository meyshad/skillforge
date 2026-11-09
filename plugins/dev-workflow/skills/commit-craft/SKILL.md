---
name: commit-craft
description: Writes precise Conventional Commits messages from the actual staged diff and splits mixed work into logical commits. Use when the user asks to commit, write or fix a commit message, squash, or "clean up" git history before a push.
---

# Commit Craft

Turn a diff into commits that a reviewer can understand in five seconds and that tooling (changelogs, semantic-release) can parse.

## Workflow

1. **Inspect, never guess.**
   - `git status --short` and `git diff --staged --stat`.
   - If nothing is staged, read `git diff --stat`, propose what to stage, and ask before staging anything that looks unrelated.
   - Read the full staged diff (`git diff --staged`) before writing a word.
2. **Learn the house style.** Run `git log -n 20 --pretty=format:%s`. If the repo already uses a convention (Conventional Commits, gitmoji, ticket prefixes like `ABC-123:`), follow it instead of the defaults below.
3. **One concern per commit.** If the diff mixes concerns (a feature + an unrelated formatting pass + a dependency bump), propose a split and use `git add -p <file>` / `git restore --staged <file>` to separate them.
4. **Write the message** using the format below.
5. **Commit** with a heredoc so newlines survive:
   ```bash
   git commit -F - <<'MSG'
   feat(auth): add refresh-token rotation

   Rotating refresh tokens on every use limits the blast radius of a
   leaked token to a single request.

   Closes #142
   MSG
   ```
6. Show the resulting `git log -1 --stat` to the user.

## Format

```
<type>(<optional scope>)<! if breaking>: <subject>

<body: what and WHY, wrapped at 72 columns>

<footers: BREAKING CHANGE:, Closes #, Refs #, Co-authored-by:>
```

| Type | Use for |
|------|---------|
| `feat` | New user-facing capability |
| `fix` | Bug fix |
| `perf` | Performance improvement with no behavior change |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `docs` | Documentation only |
| `test` | Adding or fixing tests only |
| `build` | Build system, packaging, dependencies |
| `ci` | CI configuration |
| `chore` | Maintenance that fits nothing above |
| `revert` | Reverts a previous commit (`revert: <original subject>`) |

### Subject rules
- Imperative mood: "add", not "added" / "adds". Test: *"If applied, this commit will ___"*.
- ≤ 72 characters (aim for ≤ 50), lowercase after the colon, no trailing period.
- Scope = the module, package, or area touched (`api`, `ui/button`, `deps`). Omit it if it adds nothing.
- Name the change, not the activity: `fix(cart): prevent negative quantities` beats `fix: bug fixes`.

### Body rules
- Explain **why** the change exists and any non-obvious **how**. The diff already shows *what*.
- Mention trade-offs, alternatives rejected, and follow-ups.
- Skip the body only for truly self-explanatory changes (typo fixes, version bumps).

### Breaking changes
Add `!` after the type/scope **and** a footer:
```
feat(api)!: drop support for v1 endpoints

BREAKING CHANGE: /v1/* routes now return 410 Gone. Migrate to /v2.
```

## Guardrails
- Never commit files that look like secrets (`.env`, `*.pem`, `credentials.json`, keys). Stop and warn.
- Never use `--no-verify`, `--amend` on pushed commits, or force-push unless the user explicitly asks.
- If hooks fail, fix the cause and create a **new** commit; do not bypass the hook.
- Do not invent issue numbers. Only reference issues the user or the branch name mentions.

## Examples

| Diff summary | Message |
|---|---|
| New `--json` flag on CLI | `feat(cli): add --json output flag` |
| Null check for missing avatar | `fix(profile): handle users without an avatar` |
| Replaced O(n²) loop with a map | `perf(search): index results by id to avoid quadratic scan` |
| Bumped lodash 4.17.20 → 4.17.21 | `build(deps): bump lodash to 4.17.21` |
| Renamed variables only | `refactor(billing): clarify invoice variable names` |
