---
name: holographic-memory
description: "Seed, query, and maintain Hermes holographic memory (fact_store): initial population from memory files and past sessions, ongoing fact hygiene."
triggers:
  - "seed holographic memory"
  - "fact_store"
  - "populate fact store"
  - "read memory files and seed"
  - "holographic memory not populated"
tags: [memory, fact_store, hermes, knowledge-management]
---

# Holographic Memory — Seed & Maintain

## What it is

Holographic memory is an in-session structured fact store (`fact_store` tool).
Facts survive across sessions and are injected into context. Unlike MEMORY.md /
USER.md (flat markdown), the fact store supports categories, tags, and trust
scores via `fact_feedback`.

## Seeding workflow (first use or re-seed)

Run in this order:

1. **Check current state**
   ```
   fact_store(action='list')
   ```
   If count > 0, decide whether to top-up or skip.

2. **Read memory files**
   - `/home/agas/.hermes/memories/USER.md`
   - `/home/agas/.hermes/memories/MEMORY.md`

3. **Browse past sessions**
   ```
   session_search()   # browse recent
   session_search(query="<topic>")  # targeted recall
   ```
   Pull durable facts only — skip greetings, tests, one-off task outputs.

4. **Add facts one at a time**
   ```
   fact_store(action='add', category='...', content='...', tags='...')
   ```
   See categories below.

## Categories to use

| category | what goes here |
|---|---|
| `user_pref` | communication style, workflow habits, format preferences |
| `tool` | service URLs, entity IDs, credentials hints, CLI flags |
| `general` | server inventory, project facts, repo locations |
| `project` | per-project conventions, stack, test commands |

## Pitfalls

- Do NOT add environment-state facts (e.g. "binary X not installed") — these
  go stale and cause false refusals later.
- Do NOT duplicate facts already in MEMORY.md verbatim without value-add; the
  memory files are already injected each turn. Add to fact_store when you want
  structured tags/categories for retrieval, or when the fact came from a
  session transcript not in the memory files.
- Call `fact_feedback` after using a fact to train trust scores.

## Ongoing hygiene

- After any session where new durable facts emerged, add them via `fact_store(action='add')`.
- If a fact turns out wrong, use `fact_store(action='remove', fact_id=N)`.

## Fact invalidation & bulk cleanup
- If you discover that all facts for a domain are outdated, do not keep stale ~token~ or ~entity~ entries. Remove them explicitly with `fact_store(action='remove', fact_id=N)` after listing or searching.
- If `fact_store` entries match credentials or other secrets, remove them immediately rather than flagging and leaving them in place.
- Prefer unambiguous exact text in `memory(action='remove')` when possible; if backticks/quotes or other formatting interfere, use `patch` to remove the exact lines from the underlying memory markdown files.

## Alp's initial seed (June 2026)

Seeded 12 facts from USER.md + MEMORY.md:
- 5 user preference/identity facts (fact_ids 1-5)
- 7 environment/tool facts: Home Assistant at 192.168.1.52, bird light entity,
  Radarr at 127.0.0.1:7878, server inventory path, Hermes backup repo,
  foundry server (141.144.205.247, Foundry VTT + Caddy proxy) (fact_ids 6-12)

## Alp's HA cleanup pattern (June 2026)
When the user asked to delete everything Home Assistant-related:
- All 8 `fact_store` HA entries were removed by `fact_id`.
- HA IP / token / entity entries were removed from both `~/.hermes/memories/MEMORY.md` and the backup copy at `~/Hermes/hermes-agent-backup-wacu/backup/memories/MEMORY.md`.
- Redacted `HASS_TOKEN=*** was removed from `~/.hermes/.env`.
- `fact_store` cleanup and markdown cleanup are distinct paths and should both be taken.
