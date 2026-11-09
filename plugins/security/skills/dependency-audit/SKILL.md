---
name: dependency-audit
description: Audits third-party dependencies across npm, pnpm, yarn, pip, Poetry, Go, Cargo, Ruby, PHP and Maven for known vulnerabilities, outdated or abandoned packages and license risks, then plans safe, prioritized upgrades. Use when the user asks to check dependencies, fix npm audit or Dependabot alerts, upgrade packages, or assess supply-chain risk.
---

# Dependency Audit

## 1. Detect ecosystems
Look for manifests and lockfiles at the root and in subdirectories (monorepos):

| Ecosystem | Files | Vulnerability scan | Outdated check |
|---|---|---|---|
| npm | `package-lock.json` | `npm audit --omit=dev` | `npm outdated` |
| pnpm | `pnpm-lock.yaml` | `pnpm audit --prod` | `pnpm outdated` |
| Yarn | `yarn.lock` | `yarn npm audit` (v2+) / `yarn audit` | `yarn outdated` |
| Python | `requirements*.txt`, `poetry.lock`, `uv.lock` | `pip-audit` | `pip list --outdated` |
| Go | `go.sum` | `govulncheck ./...` | `go list -u -m all` |
| Rust | `Cargo.lock` | `cargo audit` | `cargo outdated` |
| Ruby | `Gemfile.lock` | `bundle audit check --update` | `bundle outdated` |
| PHP | `composer.lock` | `composer audit` | `composer outdated` |
| Java | `pom.xml`, `build.gradle` | OWASP dependency-check | `mvn versions:display-dependency-updates` |
| Any | all of the above | `osv-scanner -r .` | n/a |

`osv-scanner` covers most ecosystems in one pass. Prefer it if available. If a tool is missing, tell the user the install command rather than skipping silently.

## 2. Triage vulnerabilities
For each advisory, record: package, installed version, fixed version, severity, **direct or transitive**, and **is it reachable?**

Prioritize by real risk, not raw CVSS:
1. Reachable + exploitable in this context (e.g. a vulnerable parser fed user input) → fix now.
2. Runtime dependency, not obviously reachable → fix this sprint.
3. Dev-only / build-only (test runners, bundlers) → batch and fix later.
4. No fix available → mitigate (input validation, config), pin, monitor, or replace the package.

`govulncheck` reports reachability natively. For others, grep for the vulnerable API usage.

## 3. Plan upgrades
- **Patch/minor** within the allowed range: usually safe. Batch them.
- **Major** versions: read the changelog or migration guide, list breaking changes that affect this codebase, upgrade one major at a time with its own commit.
- **Transitive** issues: upgrade the direct parent first; otherwise use overrides as a temporary measure (`overrides` in npm, `pnpm.overrides`, `resolutions` in Yarn, constraints files in pip) with a comment explaining why.
- Run the full test suite and build after each group. Never run `npm audit fix --force` blindly; it can install breaking majors.

## 4. Supply-chain health
Flag packages that are:
- Unmaintained (no release in 2+ years, archived repo), single-maintainer on critical paths.
- Typosquat-looking names or tiny packages with install scripts.
- Unpinned (`*`, `latest`, git branches) or missing a lockfile.
- License risk for the project's distribution model: GPL/AGPL in proprietary software, "no license", or SSPL. Use `npx license-checker --summary` or `pip-licenses`.

## 5. Report
```markdown
## Dependency audit: <date>
**Summary:** 3 critical, 5 high, 12 moderate (9 dev-only). 2 packages unmaintained.

| Priority | Package | Current | Fixed | Severity | Type | Reachable | Action |
|---|---|---|---|---|---|---|---|
| P0 | lodash | 4.17.15 | 4.17.21 | critical | direct | yes (`_.template`) | Upgrade now |

### Upgrade plan
1. Batch 1 (safe patches): ...
2. Batch 2 (major: express 4 → 5): breaking changes affecting us: ...
### Not fixable yet
- <package>: no upstream fix; mitigation: ...
```

Ask before modifying lockfiles or manifests. Make each upgrade batch a separate commit.
