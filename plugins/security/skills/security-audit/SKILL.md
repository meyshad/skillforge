---
name: security-audit
description: Runs a structured application security audit mapped to the OWASP Top 10 and CWE, combining a bundled pattern scanner with manual data-flow review of auth, input handling, secrets, crypto and configuration, and produces a prioritized, verified findings report. Use when the user asks for a security review, pentest-style code audit, vulnerability check, or hardening before launch.
---

# Security Audit

Find vulnerabilities that are **real and exploitable**, rank them by risk, and give fixes a developer can apply today.

## Phase 1: Map the attack surface (10 minutes, saves hours)
- Stack and frameworks: manifests, lockfiles, Dockerfiles, IaC.
- **Entry points:** HTTP routes, GraphQL resolvers, RPC handlers, CLI args, queue consumers, webhooks, file uploads, cron jobs.
- **Trust boundaries:** where untrusted data enters, where privileged actions happen, where data leaves (DB, shell, HTML, filesystem, outbound HTTP).
- **Assets:** credentials, PII, payment data, admin functions, tenant isolation.

## Phase 2: Automated leads
```bash
python3 scripts/scan_patterns.py . --min-severity medium   # bundled, zero-dependency
```
Plus whatever is available (all optional): `semgrep --config auto`, `bandit -r .`, `gosec ./...`, `brakeman`, `npm audit`, `pip-audit`. Run the sibling `secret-scanner` and `dependency-audit` skills if installed.

Treat every hit as a lead. **Verify by tracing data flow from source to sink.**

## Phase 3: Manual review checklist (OWASP Top 10, 2021)

**A01 Broken Access Control**
- Every state-changing and data-returning endpoint checks *who* is calling and *whether they own the object* (IDOR).
- Authorization enforced server-side, deny-by-default; no trust in client-sent roles or IDs.
- Multi-tenant queries always scoped by tenant.

**A02 Cryptographic Failures**
- Passwords hashed with argon2id / bcrypt / scrypt, never MD5/SHA*. TLS everywhere; no disabled verification.
- Sensitive data encrypted at rest where required; keys not in source.

**A03 Injection**
- SQL/NoSQL via parameterized queries or ORM bindings only. Shell via argument arrays, never string concatenation.
- Output encoding per context (HTML, attribute, JS, URL). Template auto-escaping not disabled.

**A04 Insecure Design**
- Rate limits on login, signup, password reset, OTP, and expensive endpoints. Business-logic abuse: negative quantities, coupon reuse, race conditions on balances.

**A05 Security Misconfiguration**
- Debug off in prod, no stack traces to users, security headers (CSP, HSTS, X-Content-Type-Options, frame-ancestors), restrictive CORS, default credentials removed.

**A06 Vulnerable Components**: known-CVE dependencies, unpinned versions, abandoned packages.

**A07 Identification & Authentication Failures**
- Session cookies `HttpOnly; Secure; SameSite`. Session rotation on login. MFA available for privileged users.
- Password reset tokens single-use, short-lived, unguessable. JWTs: signature verified, `alg` pinned, expiry enforced.

**A08 Software & Data Integrity Failures**: unsafe deserialization, unsigned updates, CI pulling unpinned third-party actions/scripts.

**A09 Logging & Monitoring Failures**: auth failures and admin actions logged; secrets/PII **not** logged.

**A10 SSRF**: user-supplied URLs fetched only after allow-listing scheme and host and blocking internal ranges (169.254.169.254, 10/8, 127/8, ::1).

Also check: file uploads (type, size, storage outside webroot, randomized names), path traversal, mass assignment, open redirects, XXE in XML parsers, ReDoS-prone regexes.

## Phase 4: Rate and report
Severity = impact × likelihood. Use CVSS-like reasoning but keep it human:

| Severity | Example |
|---|---|
| Critical | Unauthenticated RCE, SQLi on login, auth bypass, leaked prod credentials |
| High | IDOR exposing other users' data, stored XSS in admin panel, SSRF to cloud metadata |
| Medium | Reflected XSS needing interaction, missing rate limit on login, weak password hashing |
| Low | Missing security header, verbose errors, insecure RNG for non-security IDs |

~~~markdown
# Security Audit Report
**Scope:** <repo/commit, components reviewed>  **Date:** <date>
## Executive summary
<2–4 sentences: overall posture, count by severity, top risk.>

## Findings
### [CRITICAL] SQL injection in order search (CWE-89)
- **Location:** `api/orders.py:88`
- **Attack scenario:** `GET /orders?q=' OR 1=1--` returns every customer's orders.
- **Evidence:** user input `q` is interpolated into an f-string passed to `cursor.execute`.
- **Fix:** use a parameterized query: `cursor.execute("... WHERE name LIKE %s", (f"%{q}%",))`
- **Verification:** add a test that sends a quote character and asserts a 200 with zero leaked rows.

## Hardening recommendations
<Non-vulnerability improvements, prioritized.>
## Out of scope / not verified
<Be explicit about what you did not check.>
~~~

## Rules of engagement
- Analyze code; do not attack live systems, run exploits against third-party hosts, or exfiltrate data.
- Demonstrate exploitability with a local test or a clear request example, never with production data.
- Do not report a finding you have not traced to a reachable entry point. Label anything uncertain as "Needs verification".
