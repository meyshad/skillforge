---
name: accessibility-audit
description: Audits web UIs against WCAG 2.2 Level AA using automated tools (axe, Lighthouse) plus manual keyboard, screen-reader, contrast and semantics checks, and fixes issues in the component source. Use when the user asks about accessibility, a11y, WCAG, ADA or EAA compliance, screen reader support, keyboard navigation, or color contrast.
---

# Accessibility Audit (WCAG 2.2 AA)

Automated tools catch roughly a third of issues. Always combine them with manual checks.

## 1. Automated pass
Run whichever is available:
```bash
npx @axe-core/cli http://localhost:3000 --exit
npx lighthouse http://localhost:3000 --only-categories=accessibility --view
npx pa11y http://localhost:3000
```
In component tests: `jest-axe` / `vitest-axe`, or `@axe-core/playwright` in e2e tests. Also enable a framework linter (`eslint-plugin-jsx-a11y`, `eslint-plugin-vuejs-accessibility`, Angular ESLint template a11y rules).

## 2. Manual checks

### Keyboard (most common real-world failure)
- Every interactive element is reachable with `Tab`, operable with `Enter`/`Space`, and arrow keys work in composite widgets (menus, tabs, listboxes).
- Visible focus indicator everywhere (2.4.7), not hidden by sticky headers (2.4.11). Never `outline: none` without a replacement.
- Logical tab order; no keyboard traps; modals trap focus while open and return it on close; `Esc` closes them.
- A "Skip to main content" link exists.

### Semantics and screen readers
- Native elements first: `<button>` for actions, `<a href>` for navigation. A `div` with `onClick` is a bug.
- One `<h1>`; headings don't skip levels; landmarks (`header`, `nav`, `main`, `footer`).
- Every form control has a programmatic label (`<label for>`, `aria-labelledby`); errors are announced and associated (`aria-describedby`, `aria-invalid`).
- Images: meaningful `alt`; decorative images `alt=""`. Icon-only buttons have an accessible name.
- Dynamic updates (toasts, async results) use `aria-live` regions.
- ARIA: no ARIA is better than bad ARIA. Roles, states and properties must match the actual behavior.
- Spot-check with VoiceOver (macOS: `Cmd+F5`) or NVDA (Windows).

### Visual
- Contrast: text ≥ **4.5:1**, large text (≥ 24px, or ≥ 18.66px bold) ≥ **3:1**, UI components and focus indicators ≥ **3:1**.
- Information not conveyed by color alone (add icons or text to error states and charts).
- Works at 200% zoom and 320px width without horizontal scrolling (reflow, 1.4.10).
- Respects `prefers-reduced-motion`; nothing flashes more than 3 times per second.
- Touch/click targets at least **24×24 CSS px** (2.5.8).

### WCAG 2.2 additions to check
- 2.4.11 Focus not obscured · 2.5.7 Dragging alternatives · 2.5.8 Target size · 3.2.6 Consistent help · 3.3.7 Redundant entry · 3.3.8 Accessible authentication (no cognitive tests like puzzles without an alternative; allow paste and password managers).

## 3. Fix in source
Fix in the shared component (Button, Modal, Input) rather than per page, so one change fixes every instance. Show diffs, e.g.:
```diff
- <div className="btn" onClick={save}><Icon name="save" /></div>
+ <button type="button" className="btn" onClick={save} aria-label="Save draft">
+   <Icon name="save" aria-hidden="true" />
+ </button>
```

## 4. Report
| # | Issue | WCAG SC | Level | Impact | Location | Fix |
|---|---|---|---|---|---|---|
| 1 | Icon button has no name | 4.1.2 Name, Role, Value | A | Critical | `Toolbar.tsx:31` | Add `aria-label` |

Order by user impact (blocks a task → degrades → annoys). State what was tested (pages, browsers, assistive tech) and what wasn't. Never claim legal "compliance"; report conformance findings.
