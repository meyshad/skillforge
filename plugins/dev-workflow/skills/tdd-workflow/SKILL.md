---
name: tdd-workflow
description: Implements features and bug fixes test-first using the red, green, refactor cycle, detecting the project's existing test framework and conventions. Use when the user asks for TDD, test-first development, to "add tests", or to implement behavior that must be reliably verified.
---

# Test-Driven Development

## 0. Discover the test setup
Before writing a test, find how this project tests:
- Config: `package.json` scripts, `jest.config.*`, `vitest.config.*`, `pytest.ini`/`pyproject.toml`, `go.mod`, `Cargo.toml`, `phpunit.xml`, `*.csproj`.
- Existing tests: mirror their location, naming, fixtures, and assertion style exactly.
- Find the single-test command (e.g. `npx vitest run path -t "name"`, `pytest path::test_name`, `go test ./pkg -run TestName`).

## 1. 🔴 Red: write one failing test
- Test **one behavior**, named as a sentence: `returns_404_when_order_belongs_to_another_user`.
- Structure with Arrange, Act, Assert. One logical assertion per test.
- Run it and **confirm it fails for the right reason** (an assertion failure, not an import error or typo).

## 2. 🟢 Green: make it pass with the simplest code
- Write the minimum production code that passes. Hard-coding is fine at this step; the next test will force generalization.
- Run the test, then the surrounding suite.

## 3. 🔵 Refactor
- With tests green, remove duplication and improve names and structure in **both** production and test code.
- Re-run tests after every refactor step.

## 4. Repeat
Pick the next test from a list you keep up to date:
1. Happy path
2. Boundaries: empty, one, many, max, zero, negative
3. Invalid input and error handling
4. Edge cases specific to the domain (time zones, currency rounding, unicode)

## Test quality rules
- **Test behavior, not implementation.** Assert on outputs and observable side effects, not private methods or call counts (unless the call *is* the behavior, e.g. "sends an email").
- **Mock at the boundary only:** network, clock, filesystem, randomness, third-party APIs. Don't mock the code you own just to isolate it.
- **Deterministic:** inject a clock and seed randomness; never `sleep` in tests; no reliance on test order.
- **Fast:** unit tests in milliseconds; push slow paths into a clearly marked integration suite.
- **Readable failures:** the failure message alone should tell you what broke.

## For bug fixes
1. Write a test that reproduces the bug and fails.
2. Fix the bug.
3. The test passes and stays forever as a regression guard.

## Reporting
Show the user the red output, the green output, and the final full-suite result. Never claim tests pass without having run them.
