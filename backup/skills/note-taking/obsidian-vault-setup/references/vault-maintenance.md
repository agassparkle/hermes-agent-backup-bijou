# Vault Maintenance Guide

> The complete 8-rule maintenance playbook for any Hermes vault.

## The Rules

1. Before working in the vault, read: AGENTS.md → index.md → the relevant folder's index.md.
2. Use the vault actively — Inbox = unprocessed, Journal = today, Projects = outcomes.
3. Do not dump everything into Inbox if the destination is obvious.
4. When creating, renaming, moving, or deleting a note: update the relevant index.md in the same pass, add wikilinks where useful, keep the folder tree shallow.
5. Keep canonical tasks in Projects or Areas. Journal is not the source of truth.
6. Keep Hermes memory short. Put rich long-term context in vault notes. Memory should only point to the right note.
7. Never invent facts. If unknown, write "Unknown" or ask.
8. At the end of meaningful work, leave a short trail: what changed, where the artifact lives, next action if any.

## The Layer Model

| Layer | Holds |
|---|---|
| **memory** | Short, durable preferences and pointers |
| **AGENTS.md** | Vault operating rules |
| **Directory/** | People, companies, agents, machines, repos |
| **Projects/** | Outcome-oriented active work |
| **Areas/** | Ongoing responsibilities |
| **Journal/** | Today's execution view |
| **Wiki/** | Agent-synthesized knowledge |
| **Resources/** | Raw references |

**Memory is the index. Vault is the book.**

## Bootstrap Message

When onboarding a new Hermes instance to a vault:

```
You are [Agent Name], [Owner Name]'s execution agent.

Your durable working filesystem is this vault.

Before editing vault content:
1. Read AGENTS.md.
2. Read index.md.
3. Read the relevant directory index.

Use the vault as long-term working context:
- Projects = active outcomes
- Areas = ongoing responsibilities
- Resources = reference
- Directory = people/companies/agents/machines/repos
- Journal = today's execution view
- Inbox = unprocessed capture
- Wiki = synthesized knowledge

Keep memory short. Put rich context in vault notes.
When you create or move a note, update the relevant index in the same pass.
```
