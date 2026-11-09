---
name: pr-description
description: Writes reviewer-friendly pull request titles and descriptions from the branch's real commits and diff, including testing steps, risk and rollback. Use when the user asks to open, draft, describe or summarize a pull request or merge request.
---

# Pull Request Description

A great PR description lets a reviewer decide in under a minute **what** changed, **why**, **how to verify it**, and **what could break**.

## Workflow

1. **Find the base branch.** Prefer the repo default: `git symbolic-ref refs/remotes/origin/HEAD --short` (fall back to `main`/`master`).
2. **Collect facts:**
   ```bash
   git log --oneline <base>..HEAD
   git diff --stat <base>...HEAD
   git diff <base>...HEAD
   ```
3. **Look for a template:** `.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE/`, `docs/pull_request_template.md`. If one exists, fill **it** rather than the template below.
4. **Find context:** linked issue in the branch name (`feature/123-x`), commit footers, or ask the user.
5. **Draft** the title and body, then show them to the user before creating anything.
6. **Create** only when asked, e.g. `gh pr create --title "..." --body-file pr.md` (add `--draft` if work is incomplete).

## Title
- Same rules as a commit subject: imperative, specific, ≤ 72 chars.
- Use Conventional Commits style if the repo squash-merges with PR titles: `feat(search): add fuzzy matching`.

## Body template

```markdown
## Summary
<1–3 sentences: what this PR does, in plain language.>

## Why
<The problem, user impact, or ticket. Link: Closes #123>

## Changes
- <Grouped, high-signal bullets. Not a copy of the commit list.>
- <Call out anything surprising: new dependency, migration, config flag.>

## How to test
1. <Exact commands or click-path a reviewer can follow>
2. <Expected result>

## Screenshots / recordings
<Before/after for any UI change. Delete the section if not applicable.>

## Risk & rollback
- Risk: <low/medium/high + why>
- Rollback: <revert the PR / disable flag `X` / run down-migration>

## Checklist
- [ ] Tests added or updated
- [ ] Docs / changelog updated
- [ ] No secrets, debug code or TODOs left behind
```

## Writing rules
- Lead with impact, not implementation details.
- Every claim must come from the diff or the user. Do not claim tests were run unless you ran them and saw them pass.
- Point reviewers to the risky parts: "Start with `src/billing/proration.ts`; everything else is mechanical."
- Large PR (> ~400 changed lines)? Suggest splitting it, or add a "Review guide" section with a suggested file order.
- Mark breaking changes loudly with a `> [!WARNING]` callout and migration steps.
