---
name: readme-architect
description: Writes or overhauls a project README that converts visitors into users and contributors, with a sharp value proposition, working quickstart, badges, usage examples and contribution guide, all verified against the real code. Use when the user asks to write, improve or review a README, prepare a repo for open-source launch, or make a project more attractive on GitHub.
---

# README Architect

A visitor decides in about **10 seconds** whether your project is worth their time. The README's job is to win those 10 seconds and then get them to a working result in under 5 minutes.

## 1. Research before writing
- Read manifests, entry points, CLI `--help`, config files, examples and tests to learn what the project *actually* does.
- Identify: the target user, the problem, the "aha" moment, install method(s), minimal working example.
- **Run the quickstart yourself** where possible. Every command in the README must work as written.

## 2. Structure (adapt; drop sections that don't apply)

```markdown
<div align="center">
  <img src="docs/assets/logo.svg" width="96" alt="" />
  <h1>ProjectName</h1>
  <p><b>One sentence: what it does and for whom.</b></p>
  <!-- badges: CI · version · license · downloads · stars -->
</div>

<!-- Hero visual: GIF/screenshot of the "aha" moment, ≤ 5 MB -->

## Why ProjectName?
3–5 bullets of outcomes, not features. "Ship X in 5 minutes", "Zero config".

## Quick start
<install + the smallest example that produces a visible result, copy-paste ready>

## Usage
<the 3–5 most common tasks, each with a short example and its output>

## Features / Comparison (optional)
<table vs. alternatives, if honest and useful>

## Configuration
<table: option | default | description>

## Documentation · FAQ · Roadmap
## Contributing
<link to CONTRIBUTING.md; "good first issue" label>
## License
```

## 3. Writing rules
- **First line wins.** "Fast, type-safe SQL query builder for TypeScript" beats "A library for databases".
- Show, then tell: a code block or GIF before paragraphs of explanation.
- Copy-paste ready code blocks with language tags; show expected output.
- Use tables for options, collapsible `<details>` for long reference material.
- Scannable: short paragraphs, meaningful headings (they become the GitHub outline/TOC).
- Badges: 3–6 meaningful ones (CI, version, license, downloads). No badge walls.
- Accessibility: alt text on images, don't convey meaning by emoji or color alone.
- Relative links for repo files so they work on forks and branches.
- Offer translations as `README.<lang>.md` with a language switcher at the top.

## 4. Launch extras (for open-source growth)
- Repo **About** description + 5–10 topics (GitHub search and topic pages drive discovery).
- Social preview image (1280×640) in repository settings.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, issue/PR templates, a few `good first issue`s.
- Star-history or "used by" section once traction exists, not before.

## 5. Final check
- [ ] Every command and code sample was run or verified against source.
- [ ] Links resolve; images load; no placeholder text left.
- [ ] Value proposition is understandable by someone outside the team.
- [ ] Renders correctly in GitHub's light **and** dark themes.
