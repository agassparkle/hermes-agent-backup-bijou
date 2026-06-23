# Vault Spec (Alp's Design)

Minimum skeleton + operating rules for a Hermes-compatible Obsidian vault.

## Structure

```
vault/
  index.md
  AGENTS.md
  Inbox/
  Journal/
  Projects/
  Areas/
  Resources/
  Archive/
  Directory/
    contacts/
    companies/
    agents/
    machines/
    repos/
  Wiki/
```

No more folders. This is enough.

## AGENTS.md (most critical file)

Hermes reads this before any vault editing. Write it short and firm:

```markdown
# Vault Guide

This vault is the working memory filesystem for [Agent Name].

**Use the vault as your durable working context. If a fact will matter next week, put it in the vault or memory. If it is long/rich/contextual, prefer the vault.**

## Destination Rules

| Source | Destination |
|---|---|
| Unprocessed capture | `Inbox/` |
| Active outcomes with an end state | `Projects/` |
| Ongoing responsibilities | `Areas/` |
| Raw/reference material | `Resources/` |
| People, companies, agents, machines, repos | `Directory/` |
| Synthesized knowledge | `Wiki/` |
| Completed/inactive | `Archive/` |
| Today's execution view | `Journal/` |

Do not dump everything into Inbox if the destination is obvious.

## Operating Rules

1. Before working in the vault, read `AGENTS.md`, `index.md`, and the relevant folder's `index.md`.
2. When creating, renaming, moving, or deleting a note: update the relevant `index.md` in the same pass, add wikilinks where useful, keep the folder tree shallow.
3. Keep canonical tasks in `Projects/` or `Areas/`. Journal can copy today's tasks, but Journal is not the source of truth.
4. Keep Hermes memory short. Put rich long-term context in vault notes. Memory should only point to the right note.
5. Never invent facts. If something is unknown, write "Unknown" or ask.
6. At the end of meaningful work, leave a short trail: what changed, where the artifact lives, next action if any.
7. Create files only when they will be useful later.
```

## 5 Identity Notes (day one)

| Note | Purpose |
|---|---|
| `Directory/agents/[agent-name].md` | Agent grounding |
| `Directory/contacts/[owner-name].md` | Owner profile |
| `Directory/machines/[machine-name].md` | Machine specs |
| `Areas/personal/index.md` | Personal preferences |
| `Projects/index.md` | Active work |

### Owner note template

```markdown
# [Name]

## Role
-

## Communication style
-

## Preferences
-

## Current priorities
-

## Do not
-

## Last updated
2026-06-20
```

This carries personal context into the vault without bloating Hermes persistent memory.

## Memory vs Vault

| Layer | What it holds |
|---|---|
| `memory` | Short, durable preferences (index-like) |
| `AGENTS.md` | Vault operating rules |
| `Directory/` | People, companies, machines, agents |
| `Projects/` | Outcome-focused active work |
| `Areas/` | Ongoing responsibilities |
| `Journal/` | Today's execution view |
| `Wiki/` | Agent-synthesized knowledge |
| `Resources/` | Raw references |

**Principle:** Memory stays short. Rich context lives in vault.

## Sync Rules (Syncthing/iCloud/Drive)

- Do NOT put a Git repo inside the vault if using Syncthing.
- Do NOT use symlinks.
- Do NOT dump large binary files casually.
- Use `Projects/foo.nosync/` folders for local-only items.

## Bootstrap Message for Hermes

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

## Philosophy

Don't chase perfect information architecture on day one. Target:
1. Agent always knows where to look
2. Owner profile is clear
3. Active projects are in one place
4. Daily execution is separate
5. Indexes stay current

The rest shapes itself through use.
