---
name: code-review
description: Performs a rigorous, prioritized code review of a diff, branch or pull request covering correctness, security, performance, readability and tests, and reports only verified findings with severity and concrete fixes. Use when the user asks to review code, a PR, a commit, or "check my changes".
---

# Code Review

Review like a senior engineer who respects the author's time: few false positives, clear priorities, concrete fixes.

## 1. Scope the review
- Default target: uncommitted changes (`git diff HEAD`), otherwise the current branch against its base (`git diff <base>...HEAD`), or a PR (`gh pr diff <n>`).
- Read the PR description or commit messages first to understand **intent**. Review against intent, not your preferences.
- Read surrounding code, not just the hunk. A bug is often in what the change *didn't* update (other callers, tests, docs, migrations).

## 2. Review passes (in order)

### Correctness (highest value)
- Logic errors, off-by-one, inverted conditions, wrong operator precedence.
- Null/undefined/empty handling; error paths; partial failures; retries that are not idempotent.
- Concurrency: races, missing locks/transactions, shared mutable state, async calls not awaited.
- API contracts: changed signatures with un-updated callers, serialization changes, backwards compatibility.
- Edge cases: empty input, huge input, unicode, time zones/DST, negative numbers, floating point money.

### Security
- Injection (SQL, shell, template, path traversal), unsafe deserialization, SSRF.
- AuthN/AuthZ: missing permission checks, IDOR (`/orders/:id` without an owner check).
- Secrets in code or logs; PII written to logs; overly broad CORS; disabled TLS verification.

### Performance
- N+1 queries, queries inside loops, missing indexes for new filters.
- Unbounded memory (loading full tables/files), accidental O(n²), missing pagination.
- Blocking calls on hot or async paths; missing timeouts on network calls.

### Tests
- Does a test fail without this change and pass with it?
- Are edge cases and failure paths tested, not just the happy path?
- Flaky patterns: sleeps, real network, time-dependent assertions, order-dependent tests.

### Maintainability (lowest priority, keep brief)
- Naming that hides intent, dead code, duplicated logic that already exists in the codebase, misleading comments.

## 3. Verify before reporting
For every candidate finding, confirm it is real: trace the call path, check whether it's handled elsewhere, run the test or a quick script if possible. **Drop anything you cannot substantiate.** One verified bug beats ten speculative ones.

## 4. Severity

| Level | Meaning | Merge? |
|---|---|---|
| 🔴 **Blocker** | Bug, data loss, security hole, broken build | Must fix |
| 🟠 **Major** | Likely bug under realistic conditions, missing critical test | Should fix |
| 🟡 **Minor** | Edge case, perf concern, confusing code | Fix or follow-up |
| ⚪ **Nit** | Style, naming. Max 3 nits per review | Optional |

## 5. Output format

~~~markdown
## Review summary
<Verdict: Approve / Approve with comments / Request changes. 1–2 sentences.>

## Findings
### 🔴 1. <short title> (`path/to/file.ts:42`)
**Problem:** <what breaks and when, concrete scenario>
**Fix:**
```diff
- if (user.role = "admin") {
+ if (user.role === "admin") {
```

### 🟠 2. ...

## What's good
<1–3 specific things done well. Be genuine, not generic.>
~~~

## Etiquette
- Critique code, not people. Prefer "this will throw when `items` is empty" over "you forgot".
- Ask questions when intent is unclear instead of asserting a bug.
- Don't request rewrites outside the PR's scope; suggest a follow-up issue instead.
