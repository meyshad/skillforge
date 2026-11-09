---
name: safe-refactor
description: Restructures code without changing its behavior by first pinning behavior with characterization tests and then applying small, individually verified refactoring steps. Use when the user asks to refactor, clean up, simplify, modernize, split a large file or function, or pay down tech debt.
---

# Safe Refactoring

A refactor that changes behavior is a bug. Keep behavior identical and prove it at every step.

## 1. Establish a safety net
- Run the existing tests and record the baseline (pass count, failures that already existed).
- If coverage of the target code is weak, write **characterization tests** first: call the code with representative inputs and assert on whatever it currently returns, even if that looks wrong. Note suspected bugs separately; do **not** fix them during the refactor.
- For code with no testable seams, snapshot outputs (golden files) or log-compare before/after.

## 2. Plan the moves
State the goal in one sentence ("split `OrderService` so pricing can be tested in isolation") and list the steps. Prefer named, mechanical refactorings:

| Smell | Refactoring |
|---|---|
| Long function | Extract Function, Decompose Conditional |
| Huge class / file | Extract Class, Move Function, split by responsibility |
| Duplicated logic | Extract and reuse; check the codebase for an existing helper first |
| Long parameter list | Introduce Parameter Object |
| Nested conditionals | Guard Clauses, Replace Conditional with Polymorphism / lookup table |
| Magic values | Introduce named constants or enums |
| Primitive obsession | Introduce value types (`Email`, `Money`) |
| Shotgun surgery | Move related behavior together |
| Feature envy | Move the function to the data it uses |

## 3. Execute in small steps
For **each** step:
1. Make one mechanical change.
2. Run the tests (and type checker / linter).
3. If green, consider a commit (`refactor(scope): extract price calculation`). If red, revert the step instead of debugging forward.

Rules:
- Never mix a refactor with a feature or bug fix in the same commit.
- Keep public APIs stable; if one must change, add the new API, migrate callers, then remove the old one (expand → migrate → contract).
- Use IDE/LSP-aware renames or exhaustive `grep -rn` to update every reference, including strings, configs, docs, and reflection/dynamic usage.

## 4. Verify
- Full test suite, type check, lint, and build all match or beat the baseline.
- Diff review: the change should read as pure restructuring. Point out any line that could alter behavior.

## 5. Report
- What changed structurally and why it's better (testability, readability, coupling).
- Metrics if useful: function length, file size, cyclomatic complexity before → after.
- Suspected pre-existing bugs found along the way (kept unchanged, listed for follow-up).
