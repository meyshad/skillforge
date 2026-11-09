---
name: incident-postmortem
description: Facilitates blameless incident postmortems by reconstructing an accurate timeline from logs, alerts, deploys and chat, analyzing contributing factors, and producing owned, measurable action items. Use after an outage, production incident, data issue or near miss, or when the user asks for a postmortem, RCA, incident report or retrospective.
---

# Incident Postmortem

The goal is **learning, not blame**. Systems and processes fail; people act reasonably on the information they had.

## 1. Gather facts
Ask the user for, or read from what's available:
- Alert and monitoring data, error rates, latency graphs.
- Deploy and change history around the window: `git log --since="<start>" --until="<end>"`, CI/CD runs, feature-flag changes, config and infra changes.
- Application logs and traces. Support tickets and customer reports.
- The incident chat channel or call notes (who saw what, when, and what they did).

Normalize every timestamp to one timezone (UTC) and mark each entry's source.

## 2. Reconstruct the timeline
| Time (UTC) | Event | Source |
|---|---|---|
| 14:02 | Deploy `v2.31.0` rolls out to 100% | CD pipeline |
| 14:09 | p99 latency on `/checkout` > 4s | Grafana |
| 14:15 | First alert pages on-call | PagerDuty |
| 14:31 | Rollback started | Chat |
| 14:38 | Metrics recover | Grafana |

Derive the key metrics: **time to detect** (start → alert), **time to mitigate**, **time to resolve**, customer impact (users, requests, revenue, SLO budget burned).

## 3. Analyze contributing factors
- Use the **5 Whys** on the trigger, but expect multiple branches: incidents rarely have a single root cause.
- Look at four layers: **trigger** (what changed), **vulnerability** (why the system couldn't tolerate it), **detection** (why we didn't notice sooner), **response** (what slowed mitigation).
- Ask "how did this make sense at the time?" for every human decision.
- Note what went **well** too: those are practices to reinforce.

## 4. Action items
Each item must be **specific, owned, prioritized and dated**:

| Action | Type | Owner | Priority | Due | Ticket |
|---|---|---|---|---|---|
| Add load test for checkout to the release pipeline | Prevent | @team-payments | P1 | 2026-04-01 | PAY-812 |
| Alert on p99 > 2s for 3 min (was 10 min) | Detect | @sre | P1 | 2026-03-20 | SRE-77 |
| One-click rollback in deploy tool | Mitigate | @platform | P2 | 2026-04-15 | PLT-301 |

Avoid vague items like "be more careful" or "improve monitoring".

## 5. Document template
```markdown
# Postmortem: <short title> (<YYYY-MM-DD>)
**Status:** Draft | Reviewed  **Severity:** SEV-1/2/3  **Authors:** <names>
## Summary
<3–4 sentences: what happened, impact, duration, how it was resolved.>
## Impact
<users affected, error rate, duration, SLO budget consumed, data loss yes/no>
## Timeline
<table from step 2>
## Contributing factors
<trigger, vulnerability, detection, response>
## What went well
## What was difficult / where we got lucky
## Action items
<table from step 4>
## Lessons learned
```

## Language rules
- Blameless wording: "the deploy pipeline allowed an untested migration", not "Bob ran a bad migration".
- Name roles, not individuals, in the analysis sections.
- State uncertainty explicitly ("we believe", "not yet confirmed") and list open questions.
