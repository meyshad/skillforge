---
name: changelog-keeper
description: Maintains a human-readable CHANGELOG.md in Keep a Changelog format from git history, suggests the next Semantic Version from Conventional Commits, and drafts release notes. Use when the user asks to update the changelog, prepare a release, bump a version, or write release notes.
---

# Changelog Keeper

Changelogs are for **humans**: users deciding whether to upgrade. Not a dump of `git log`.

## 1. Generate a draft
```bash
# Since the latest tag, with links and an automatic SemVer suggestion
python3 scripts/changelog.py --version auto --repo-url https://github.com/OWNER/REPO

# Explicit range and version
python3 scripts/changelog.py --from v1.4.0 --to HEAD --version 1.5.0
```
`scripts/` is relative to this skill's directory. The script maps Conventional Commit types to sections:

| Commit type | Section |
|---|---|
| `feat` | Added |
| `fix` | Fixed |
| `fix(security)` / `security` | Security |
| `perf`, `refactor` | Changed |
| `revert` | Removed |
| `type!` or `BREAKING CHANGE:` footer | ⚠ BREAKING CHANGES |
| `docs`, `test`, `ci`, `build`, `chore`, `style` | omitted (use `--all` to include) |

If the history doesn't follow Conventional Commits, read `git log --oneline <last-tag>..HEAD` and classify commits manually.

## 2. Edit the draft like an editor
- Rewrite entries in user language: ~~"refactor UserSvc DI"~~ → "Faster startup when many plugins are installed".
- Merge related commits into one entry; drop noise (typo fixes, reverts of unreleased work).
- Every breaking change gets a one-line **migration instruction**.
- Keep newest version at the top. Keep an `## [Unreleased]` section between releases.

## 3. CHANGELOG.md format
```markdown
# Changelog
All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.5.0] - 2026-03-14
### Added
- **export:** CSV export for reports (#231)
### Fixed
- Dates no longer shift by one day for users west of UTC (#240)

[Unreleased]: https://github.com/OWNER/REPO/compare/v1.5.0...HEAD
[1.5.0]: https://github.com/OWNER/REPO/compare/v1.4.0...v1.5.0
```
Update the compare links at the bottom on every release.

## 4. Choose the version (SemVer)
- **MAJOR**: any breaking change to the public API, CLI flags, config format or behavior users rely on.
- **MINOR**: new backwards-compatible functionality.
- **PATCH**: backwards-compatible bug fixes only.
- Pre-1.0: breaking changes bump MINOR (`0.4.2 → 0.5.0`).

## 5. Release checklist (only with the user's go-ahead)
1. Move `[Unreleased]` entries under the new version heading with today's date.
2. Bump the version in manifests (`package.json`, `pyproject.toml`, `Cargo.toml`, ...).
3. Commit: `chore(release): v1.5.0`.
4. Tag: `git tag -a v1.5.0 -m "v1.5.0"`.
5. Push and publish: `git push --follow-tags`, then `gh release create v1.5.0 --notes-file notes.md`.

Release notes = the changelog section, plus a short highlight paragraph and upgrade notes at the top.
