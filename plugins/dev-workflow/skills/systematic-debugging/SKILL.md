---
name: systematic-debugging
description: Finds the root cause of bugs with a disciplined reproduce, isolate, hypothesize, verify loop (including git bisect) instead of guess-and-patch, then locks the fix in with a regression test. Use when the user reports a bug, crash, failing test, flaky behavior, regression, or "it works on my machine".
---

# Systematic Debugging

**Rule zero:** do not change code until you can explain the bug. Patches applied to symptoms create new bugs.

## The loop

### 1. Reproduce
- Get the exact failing command, input, environment and the **full** error output (stack trace, logs, exit code).
- Turn it into a one-command reproduction: a failing test, a script, or a `curl`. Run it and watch it fail.
- Can't reproduce? Diff the environments: versions (`node -v`, `python -V`, lockfile), env vars, config, data, OS, time zone, locale, concurrency/load.

### 2. Minimize
- Shrink the input and the code path until removing anything else makes the bug disappear.
- Binary-search the problem space: comment out halves, feed half the data, disable half the middleware.

### 3. Locate in history (for regressions)
If it used to work, let git find the commit:
```bash
git bisect start
git bisect bad                 # current commit is broken
git bisect good <last-good-sha-or-tag>
git bisect run ./repro.sh      # script exits 0 = good, 1 = bad, 125 = skip
git bisect reset
```

### 4. Hypothesize and test
- Write down 2–3 candidate explanations ranked by likelihood.
- For each one, design an observation that would **disprove** it (a log line, a breakpoint, an assertion, a print of the actual value and type).
- Change **one variable at a time**. Record what you tried and what you saw.
- Read the error message literally and fully. Check the *first* error in the log, not the last.

### 5. Fix the root cause
- Ask "why?" until you reach a cause you can control (the 5 Whys). Example: *crash → null user → session expired → token TTL shorter than cache TTL → fix TTL alignment*, not *add a null check*.
- Search for the same pattern elsewhere: `grep -rn "<the buggy pattern>"`. Fix all instances or list them.

### 6. Prove it
- The reproduction from step 1 now passes. Commit it as a **regression test**.
- Run the full relevant test suite to catch collateral damage.
- Remove temporary logging and debug flags.

### 7. Report
```markdown
**Symptom:** <what the user saw>
**Root cause:** <the actual defect, with file:line>
**Why it happened:** <the chain of events>
**Fix:** <what changed and why it addresses the cause>
**Prevention:** <regression test added, lint rule, monitoring>
```

## Common culprits checklist
- Stale caches or build artifacts (`rm -rf node_modules/.cache dist`, rebuild).
- Wrong version actually running (check what is installed, not what's in the manifest).
- Async: un-awaited promise, missing `return`, race between two writers.
- Mutable shared state or default-mutable arguments.
- Time: time zones, DST, clock skew, `Date` month index starting at 0.
- Encoding: UTF-8 vs Latin-1, BOM, CRLF vs LF.
- Floating point comparison and rounding.
- Environment: missing env var silently defaulting to something.

## Flaky tests
Run the test in a loop to measure the failure rate (`for i in $(seq 50); do <cmd> || echo FAIL; done`). Look for ordering dependence (run in random order / isolation), shared fixtures, real time, real network, and unawaited async work.
