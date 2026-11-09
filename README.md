<div align="center">

# ⚒️ SkillForge

**Agent Skills for serious software engineering.**<br/>
18 tested skills that turn your AI coding agent into a disciplined senior engineer:<br/>
clean commits, real code reviews, root-cause debugging, security audits, production Docker and CI.

[![Validate](https://github.com/meyshad/skillforge/actions/workflows/validate.yml/badge.svg)](https://github.com/meyshad/skillforge/actions/workflows/validate.yml)
[![Skills](https://img.shields.io/badge/skills-18-6f42c1)](#-skill-catalog)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![GitHub stars](https://img.shields.io/github/stars/meyshad/skillforge?style=social)](https://github.com/meyshad/skillforge/stargazers)

**English** · [فارسی](README.fa.md)

</div>

---

## Why SkillForge?

AI coding agents are fast, but left alone they guess. They write vague commit messages, "fix" symptoms instead of causes, approve PRs without reading the callers, and ship Dockerfiles running as root.

**Skills fix that.** A skill is a folder with a `SKILL.md` playbook (plus optional scripts) that the agent loads automatically when a task matches. SkillForge packs proven engineering practice into skills that are:

- 🎯 **Opinionated and specific.** Concrete steps, commands, checklists and output formats, not vague advice.
- ✅ **Verification-first.** Every skill ends with "prove it": run the tests, measure, trace the data flow. No unverified claims.
- 🛠️ **Backed by real tools.** Zero-dependency Python scanners for secrets and dangerous code patterns, plus a changelog generator, all unit-tested.
- 🔌 **Portable.** Plain `SKILL.md` folders following the open Agent Skills format. One-command install for Claude Code (as a plugin marketplace), Codex CLI, or any agent that reads skill folders.
- 🧩 **Modular.** Five plugins. Install only what you need.

## 📦 Skill catalog

### 🧑‍💻 `dev-workflow`: everyday engineering
| Skill | What it does |
|---|---|
| [commit-craft](plugins/dev-workflow/skills/commit-craft/SKILL.md) | Conventional Commits from the real diff; splits mixed work into logical commits |
| [pr-description](plugins/dev-workflow/skills/pr-description/SKILL.md) | Reviewer-friendly PRs with testing steps, risk and rollback |
| [code-review](plugins/dev-workflow/skills/code-review/SKILL.md) | Prioritized, verified findings across correctness, security, performance and tests |
| [systematic-debugging](plugins/dev-workflow/skills/systematic-debugging/SKILL.md) | Reproduce → isolate → `git bisect` → root cause → regression test |
| [tdd-workflow](plugins/dev-workflow/skills/tdd-workflow/SKILL.md) | Red, green, refactor using your project's existing test stack |
| [safe-refactor](plugins/dev-workflow/skills/safe-refactor/SKILL.md) | Characterization tests first, then small verified behavior-preserving steps |

### 🔐 `security`: find it before attackers do
| Skill | What it does |
|---|---|
| [security-audit](plugins/security/skills/security-audit/SKILL.md) | OWASP Top 10 / CWE audit with a bundled pattern scanner (30+ rules, 8 languages) |
| [secret-scanner](plugins/security/skills/secret-scanner/SKILL.md) | Finds leaked keys and tokens in files **and git history**, then guides rotation |
| [dependency-audit](plugins/security/skills/dependency-audit/SKILL.md) | CVE triage by reachability, safe upgrade plans, license and supply-chain checks |

### 📚 `docs`: documentation people actually read
| Skill | What it does |
|---|---|
| [readme-architect](plugins/docs/skills/readme-architect/SKILL.md) | READMEs that convert visitors into users, with every command verified |
| [changelog-keeper](plugins/docs/skills/changelog-keeper/SKILL.md) | Keep a Changelog + SemVer bump suggestion, generated from Conventional Commits |
| [adr-writer](plugins/docs/skills/adr-writer/SKILL.md) | Architecture Decision Records (MADR) with honest trade-offs |
| [api-docs](plugins/docs/skills/api-docs/SKILL.md) | OpenAPI 3.1 specs derived from real route handlers and validators |

### 🚀 `devops`: ship it safely
| Skill | What it does |
|---|---|
| [dockerize](plugins/devops/skills/dockerize/SKILL.md) | Multi-stage, non-root, cache-friendly Dockerfiles for Node, Python and Go |
| [github-actions](plugins/devops/skills/github-actions/SKILL.md) | Fast CI with SHA-pinned actions, least privilege, OIDC and injection-safe scripts |
| [incident-postmortem](plugins/devops/skills/incident-postmortem/SKILL.md) | Blameless postmortems with timelines and owned, dated action items |

### 🎨 `frontend`: fast and accessible
| Skill | What it does |
|---|---|
| [accessibility-audit](plugins/frontend/skills/accessibility-audit/SKILL.md) | WCAG 2.2 AA audit: axe + keyboard, screen reader and contrast checks, fixes in source |
| [web-performance](plugins/frontend/skills/web-performance/SKILL.md) | Core Web Vitals (LCP, INP, CLS): measure, fix the biggest bottleneck, re-measure |

## ⚡ Quick start

### Option 1: Claude Code plugin marketplace
```text
/plugin marketplace add meyshad/skillforge
/plugin install dev-workflow@skillforge
/plugin install security@skillforge
```
Available plugins: `dev-workflow`, `security`, `docs`, `devops`, `frontend`.

### Option 2: one-line installer (any supported agent)
```bash
curl -fsSL https://raw.githubusercontent.com/meyshad/skillforge/main/scripts/install.sh | bash
```
```bash
# Pick a target and a subset
./scripts/install.sh --target codex --plugin security     # ~/.codex/skills
./scripts/install.sh --project --skill code-review        # ./.claude/skills in the current repo
./scripts/install.sh --dir ~/my-agent/skills              # any agent that reads SKILL.md folders
./scripts/install.sh --list                               # see everything
./scripts/install.sh --uninstall --plugin frontend
```

### Option 3: manual
Copy any folder from `plugins/*/skills/` into your agent's skills directory. Each skill is self-contained.

## 🧠 How it works

```
You:   "review my changes before I open the PR"
Agent: matches the `code-review` skill description → loads SKILL.md
       → scopes the diff → runs correctness/security/perf/test passes
       → verifies each finding → reports by severity with concrete fixes
```

Only the short `description` of each skill sits in the agent's context. The full playbook loads **on demand**, so installing all 18 skills costs almost nothing until one is needed. You can also invoke a skill by name: *"use the secret-scanner skill on this repo"*.

## 🔧 Bundled tools (usable on their own)

```bash
# Hard-coded secrets in files and full git history (exit 1 on findings, CI-friendly)
python3 plugins/security/skills/secret-scanner/scripts/scan_secrets.py . --history

# First-pass SAST: eval, shell injection, SQL concatenation, unsafe deserialization, TLS off, ...
python3 plugins/security/skills/security-audit/scripts/scan_patterns.py . --min-severity high

# Changelog section + next SemVer from Conventional Commits
python3 plugins/docs/skills/changelog-keeper/scripts/changelog.py --version auto
```
Python 3.8+ standard library only. No `pip install`.

## 🗂️ Repository layout
```
.claude-plugin/marketplace.json   # plugin marketplace manifest
plugins/<plugin>/
  .claude-plugin/plugin.json      # plugin manifest
  skills/<skill>/SKILL.md         # the playbook (YAML frontmatter + instructions)
  skills/<skill>/scripts/         # optional helper tools
scripts/install.sh                # cross-agent installer
scripts/validate.py               # structure + frontmatter validator (runs in CI)
template/SKILL.md                 # starting point for new skills
tests/                            # unit tests for bundled tools
```

## 🤝 Contributing
New skills and improvements are very welcome. Start from [`template/SKILL.md`](template/SKILL.md), read the [skill authoring guide](docs/writing-skills.md), and run:
```bash
python3 scripts/validate.py && python3 -m unittest discover tests
```
See [CONTRIBUTING.md](CONTRIBUTING.md) for details. Ideas: open an issue with the **Skill request** template.

## 🗺️ Roadmap
- [ ] `database` plugin: migration review, query optimization, index advisor
- [ ] `mobile` plugin: React Native / Flutter release checklists
- [ ] `ai-engineering` plugin: prompt evaluation, RAG debugging
- [ ] Skill evaluation suite (before/after task benchmarks)

## ⭐ Star history
If SkillForge saves you time, a star helps others find it.

[![Star History Chart](https://api.star-history.com/svg?repos=meyshad/skillforge&type=Date)](https://star-history.com/#meyshad/skillforge&Date)

## License
[MIT](LICENSE) © 2026 Meyshad
