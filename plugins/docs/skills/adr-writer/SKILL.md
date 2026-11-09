---
name: adr-writer
description: Records significant technical decisions as Architecture Decision Records (MADR format) with context, options considered, trade-offs and consequences, and keeps the ADR log numbered and linked. Use when the user is choosing between technologies or designs, asks to document a decision, write an ADR or RFC, or explain why the system is built a certain way.
---

# Architecture Decision Records

An ADR captures **why** a decision was made, so future engineers don't have to guess, re-litigate it, or repeat a failed experiment.

## When to write one
Write an ADR when a decision is hard to reverse or affects many people: choosing a database, framework, or cloud service; an API style; a module boundary; an auth approach; a build/deploy strategy; adopting or dropping a major dependency. Skip it for easily reversible, local choices.

## Workflow
1. **Find the log.** Look for `docs/adr/`, `docs/decisions/`, `adr/` or `architecture/decisions/`. Create `docs/adr/` if none exists, with a `README.md` index.
2. **Number it.** Next sequential number, zero-padded: `0007-use-postgres-for-event-store.md`. Titles are short, present-tense decisions.
3. **Gather context.** Ask the user for constraints you can't infer: team skills, budget, scale, deadlines, compliance. Read the relevant code to describe the current state accurately.
4. **Present real options.** At least two plus "do nothing" where reasonable. Evaluate each against the same decision drivers.
5. **Write it** with the template below. Keep it to one or two pages.
6. **Link it.** Add it to the index; if it replaces an earlier ADR, mark the old one `Superseded by ADR-00NN` and link both ways. Never edit an accepted ADR's decision; supersede it.

## Template (MADR)

```markdown
# ADR-0007: Use PostgreSQL for the event store

- **Status:** Proposed | Accepted | Deprecated | Superseded by [ADR-0012](0012-....md)
- **Date:** 2026-03-14
- **Deciders:** @alice, @bob
- **Tags:** data, persistence

## Context and problem statement
<2–5 sentences. What forces are at play? What breaks or blocks us today? Include numbers: load, data size, latency targets, team size.>

## Decision drivers
- <e.g. strong consistency for financial events>
- <operational simplicity: team already runs Postgres>
- <cost under $X/month at expected scale>

## Considered options
1. PostgreSQL with an append-only events table
2. Kafka as the source of truth
3. EventStoreDB

## Decision outcome
**Chosen: Option 1, PostgreSQL**, because <link back to the drivers>.

### Consequences
- ✅ Good: <benefit>
- ✅ Good: <benefit>
- ⚠️ Bad: <cost we accept, and how we will mitigate it>
- 🔁 Revisit if: <trigger, e.g. sustained >5k events/s>

## Pros and cons of the options
### PostgreSQL
- ✅ Transactions with existing data; team expertise
- ❌ Fan-out to consumers needs outbox/CDC
### Kafka
- ✅ High throughput, native streaming
- ❌ New operational burden; exactly-once is complex
### EventStoreDB
- ✅ Purpose-built projections
- ❌ Niche skill set; smaller ecosystem

## Links
- <benchmarks, spike PRs, vendor docs, related ADRs>
```

## Quality bar
- Context is understandable by someone who joins in two years.
- The decision is a clear sentence; consequences include the **negatives** honestly.
- Options are evaluated fairly against the same drivers; no strawmen.
- Status reflects reality; a "Proposed" ADR becomes "Accepted" only when the user confirms.
