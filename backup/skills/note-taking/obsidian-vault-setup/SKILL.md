---
name: obsidian-vault-setup
description: Set up an Obsidian vault for Hermes Agent with Git backup, Syncthing sync, and cron auto-commit. Covers NTFS/FUSE git pitfalls.
platforms: [linux]
---

# Obsidian Vault Setup for Hermes Agent

Create a new Obsidian vault integrated with Hermes, Syncthing multi-device sync, and Git backup with daily auto-commit.

## Triggers

- "Obsidian vault kur"
- "vault setup"
- "Obsidian + Hermes bağla"
- Any task creating a new vault for Hermes integration

## Prerequisites Check

Before creating the vault, verify:
1. **Syncthing is running** — `pgrep -la syncthing`
2. **Git is installed** — `git --version`
3. **GitHub token exists** — check `~/.hermes/.env` for `GITHUB_TOKEN=`
4. **SSH keys to GitHub** — `ssh -T git@github.com` (fix host key if needed: `ssh-keyscan github.com >> ~/.ssh/known_hosts`)

## Step 1: Choose Vault Path

User decides the vault location. Common patterns:
- `/mnt/sda2/Obsidian Vaults/<name>/` — existing Syncthing folder on NTFS/FUSE mount
- `/home/agas/<name>/` — local only, no sync

If path is under an existing Syncthing folder, it auto-syncs to all devices — no extra config needed.

## Step 2: Create Folder Structure

Use the Alp vault spec — a clean PARA-inspired structure optimized for agent readability:

```
vault/
├── index.md                   # Root MOC navigation
├── AGENTS.md                  # ⚠️ MOST CRITICAL — Hermes reads this first
│
├── Inbox/                     # Unprocessed capture
│   └── index.md
├── Journal/                   # Daily execution view
│   └── index.md
├── Projects/                  # Active outcomes (deadlines)
│   └── index.md
├── Areas/                     # Ongoing responsibilities (no deadline)
│   └── index.md
├── Resources/                 # Reference material
│   └── index.md
├── Archive/                   # Completed / inactive
│   └── index.md
│
├── Directory/                 # People, companies, agents, machines, repos
│   ├── index.md
│   ├── contacts/
│   │   └── index.md
│   ├── agents/
│   │   └── index.md
│   ├── machines/
│   │   └── index.md
│   ├── repos/
│   │   └── index.md
│   └── companies/
│       └── index.md
│
├── Wiki/                      # Synthesized knowledge (agent-curated)
│   └── index.md
│
└── .obsidian/                 # Obsidian config (auto-created)
```

**Key rules:**
- Every folder has an `index.md` — update it whenever adding, renaming, or removing a note.
- Keep folder trees **shallow** — no deep nesting.
- Do NOT open more folders than this. It scales with use.

Create with `mkdir -p`, then write `index.md` (root MOC) and all sub-`index.md` files.

## Step 3: Create AGENTS.md (CRITICAL)

This is the **most important file** in the vault. Hermes reads it before any vault editing. Write it at vault root:

```markdown
# Vault Guide

This vault is the working memory filesystem for Hermes (wacu).

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

1. Before working in the vault, read:
   - `AGENTS.md`
   - `index.md`
   - the relevant folder's `index.md`

2. When creating, renaming, moving, or deleting a note:
   - update the relevant `index.md` in the same pass
   - add wikilinks like `[[note-name]]` where useful
   - keep the folder tree shallow

3. Keep canonical tasks in `Projects/` or `Areas/`.
   Journal can copy today's tasks, but **Journal is not the source of truth**.

4. **Keep Hermes memory short.** Put rich long-term context in vault notes. Memory should only point to the right note.

5. **Never invent facts.** If something is unknown, write "Unknown" or ask.

6. At the end of meaningful work, leave a short trail:
   - what changed
   - where the artifact/note lives
   - next action if any

7. Create files only when they will be useful later.
```

## Step 4: Create Identity Notes

Start with exactly **5 identity notes** — these ground the agent:

| Note | Path | Content |
|---|---|---|
| Agent | `Directory/agents/hermes.md` | Agent role, model, config, rules |
| Owner | `Directory/contacts/alp.md` | Role, communication style, preferences, priorities, "Do Not" list |
| Machine | `Directory/machines/home-server.md` | Hostname, OS, services, connection details |
| Areas | `Areas/personal/index.md` | Personal preferences, links to contacts note |
| Projects | `Projects/index.md` | Active projects list (start with one: vault setup) |

The **owner note** (`Directory/contacts/alp.md`) is especially important — it carries personal context into the vault without bloating Hermes persistent memory:

```markdown
# [Name]

## Role
- ...

## Communication Style
- ...

## Preferences
- ...

## Current Priorities
- ...

## Do Not
- ...

## Last Updated
2026-06-20
```

**Principle:** Memory stays short (index-like). Rich personal context lives in the vault. `memory` tool stores only durable preferences; vault stores the details.

## Step 5: Initialize Git

**PITFALL: NTFS/FUSE mounts** — if the vault is on a FUSE filesystem (e.g., NTFS via ntfs-3g), git will reject with "detected dubious ownership". Fix:

```bash
git config --global --add safe.directory "/path/to/vault"
```

Then initialize:

```bash
cd /path/to/vault
git init
git config user.name "Alp"
git config user.email "alpozben@gmail.com"
```

Create `.gitignore` excluding: `.obsidian/workspace*`, `.trash/`, `.stfolder*`, `.DS_Store`.

Make the first commit immediately to establish baseline.

## Step 5: Set Hermes Environment Variable

Add to `~/.hermes/.env`:

```bash
OBSIDIAN_VAULT_PATH=/path/to/vault
```

This is how the bundled `obsidian` skill discovers the vault. It reads from `~/.hermes/.env` at load time.

## Step 6: GitHub Remote

First, attempt API-based repo creation:

```python
# read token from ~/.hermes/.env, POST to https://api.github.com/user/repos
# body: {"name":"<vault-name>","private":true,"auto_init":false}
```

**PITFALL: Fine-grained token permissions for repo creation AND push** — fine-grained PATs need MULTIPLE permissions for the full create+push workflow:

| Operation | Permission Needed |
|---|---|
| Create repo (API) | **Administration → Read and write** |
| Push code | **Contents → Read and write** |
| Both | Token must also have access to the repo: either **All repositories** or the specific repo added under "Only select repositories" |

Classic tokens just need the `repo` scope checkbox — one click, done.

**Real failure sequence encountered (June 2026):**
1. API creates repo successfully → `SUCCESS: https://github.com/agassparkle/wacu-vault` (Administration ✓)
2. Push fails → `403: Write access to repository not granted` (Contents ✗)
3. User adds Contents permission → push still fails (token scoped to "Only select repositories" but `wacu-vault` is new, not in the select list)
4. User adds the repo to the select list OR switches to "All repositories" → push succeeds
5. Post-push credential priming needed for cron job (see below)

**Token diagnostic**: to check if a token is classic or fine-grained, call `GET /user` and inspect the response headers. Classic tokens return `X-OAuth-Scopes` with comma-separated scopes. Fine-grained tokens return no `X-OAuth-Scopes` header at all. Fine-grained tokens are identified by length (typically 93+ chars for GitHub fine-grained PATs vs 40 chars for classic).

**Token tool output is REDACTED.** Hermes terminal tool displays `GITHUB_TOKEN=***` so you cannot read the token value from `cat ~/.hermes/.env` directly. The actual token value IS in the file and downstream commands receive it correctly — but you as the agent cannot see it. When writing Python scripts that read the token, use `open()` directly — the file contains the real value.

If the API call fails, tell the user to either:
1. Edit the token at https://github.com/settings/tokens → verify **Administration** + **Contents** are Read and write, AND repository access is **"All repositories"** (or the new repo is in the select list)
2. Or create the repo manually at https://github.com/new (name: `<vault-name>`, private, no README init), then share the URL

Once repo exists, add remote and push:

```bash
git remote add origin https://github.com/agassparkle/<vault-name>.git
git push -u origin master
```

If push fails with auth, use the token directly in the remote URL for the initial push, then switch to credential store:

```bash
# Read token, push with tokenized URL, then clean up
TOKEN=... # from ~/.hermes/.env
git remote set-url origin "https://${TOKEN}@github.com/user/repo.git"
git push -u origin master
# After push succeeds, remove token from URL
git remote set-url origin https://github.com/user/repo.git
```

**PITFALL: Credential store must be primed.** Setting `git config credential.helper store` alone does NOT persist credentials — it only tells git WHERE to store them. You must perform one authenticated operation (push with tokenized URL, or manually write to `~/.git-credentials`) to prime the store before the daily cron job can authenticate. If you don't prime, the cron job will fail silently every night:

```bash
# Push once with tokenized URL — this primes the store
# Then SWITCH BACK to clean URL immediately after
git remote set-url origin "https://${TOKEN}@github.com/user/repo.git"
git push -u origin master
git remote set-url origin https://github.com/user/repo.git
```

**Alternative: manually write the credential entry:**
```python
import os
token = None
with open(os.path.expanduser('~/.hermes/.env')) as f:
    for line in f:
        s = line.strip()
        if s.startswith('GITHUB_TOKEN') and '=' in s and not s.startswith('#'):
            token = s.split('=', 1)[1].strip().strip("'\"").strip()
with open(os.path.expanduser('~/.git-credentials'), 'a') as f:
    f.write(f'https://{token}:x-oauth-basic@github.com\n')
```

Verify by pushing with the clean URL after priming — should show "Everything up-to-date" with no auth prompt.

## Step 7: Daily Auto-Commit Cron Job

Create a script at `~/.hermes/scripts/<vault>-sync.sh`:

```bash
#!/bin/bash
VAULT="/path/to/vault"
cd "$VAULT" || exit 1
if [[ -z $(git status --porcelain) ]]; then
    exit 0  # No changes = silent
fi
git add -A
git commit -m "📝 Auto-commit: $(date '+%Y-%m-%d %H:%M')" >/dev/null 2>&1
git push origin master 2>&1 | tail -1
echo "✅ Vault synced: $(date '+%Y-%m-%d %H:%M')"
```

Make executable: `chmod +x`

Create the cron job:

```
cronjob action=create name="Wacu Vault Daily Git Sync" schedule="0 20 * * *" script="wacu-vault-sync.sh" no_agent=true deliver="local"
```

**PITFALL: Script path** — `script` parameter must be a filename relative to `~/.hermes/scripts/`, NOT an absolute or home-relative path. Example: `wacu-vault-sync.sh` ✓, `~/.hermes/scripts/wacu-vault-sync.sh` ✗.

**Time zone note**: Istanbul = UTC+3. `0 20 * * *` = 23:00 Istanbul time.

## Step 9: Memory → Vault Migration

After the vault is set up, migrate long memory entries into vault notes to keep Hermes persistent memory lean (target: under 50%).

### When to migrate

A memory entry is a candidate for vault migration when:
- It is **long** (200+ chars) and explains config details, troubleshooting steps, or reference material
- It describes a **server, device, or service** — these belong in `Directory/machines/`
- It documents a **pitfall, bug, or fix** — these belong in `Wiki/`
- It is **reference knowledge** (game rules, API specs, auth config) — these belong in `Resources/`
- It describes an **automation or workflow** — these belong in `Areas/`

### What stays in memory

- Short behavioral preferences (1-2 lines)
- Pointers to vault notes: `[[Wiki/some-note]]` format
- Operationally frequent facts (entity IDs, connection patterns)
- Cross-session guardrails ("don't override config defaults")

### Migration pattern

For each candidate entry:
1. Create the vault note with full detail under the right folder
2. Update the folder's `index.md` with a link to the new note
3. Replace the memory entry with a short pointer: `Topic: [[path/to/note]]. Key fact.`
4. Commit and push

### Example: Pill reminder entry

**Before** (memory, ~400 chars):
> Pill reminder (2026-06-20 rebuilt): HA automations pill_reminder_reset_daily + pill_reminder_shield_active_09_12 in automations.yaml. Shell_command pill_reminder_webhook → /config/python_scripts/pill_reminder.py → Hermes webhook pill-reminder2 (secret pill-secret-123, HMAC-SHA256 X-Webhook-Signature) at http://192.168.1.51:8644/webhooks/pill-reminder2...

**After** (memory, ~120 chars):
> Pill reminder: [[Areas/home-assistant/pill-reminder]]. Webhook pill-reminder2, secret pill-secret-123. input_boolean ile günde 1 kere. Detay vault'ta.

Full detail now lives in `Areas/home-assistant/pill-reminder.md` with architecture diagram, config files table, and pitfall notes.

### Migration checklist

- [ ] Create vault note in correct folder
- [ ] Write full detail (architecture, config, troubleshooting)
- [ ] Update folder `index.md`
- [ ] Replace memory entry with short `[[path]]` pointer
- [ ] `memory` target: remove old entry, replace with pointer
## Verification

1. `echo $OBSIDIAN_VAULT_PATH` — should show the vault path
2. Load the `obsidian` skill and test: list notes, search, create a test note
3. Check Syncthing is syncing the vault folder to other devices
4. Manual `git push` to confirm GitHub remote works
5. Cron job will fire at next scheduled time — check with `cronjob action=list`

## Support Files

- `references/vault-spec.md` — detailed vault structure specification
- `references/vault-maintenance.md` — complete 8-rule maintenance playbook + bootstrap message
- `references/memory-migration.md` — when and how to move memory entries to vault notes (concrete example)

## Pitfalls

| Pitfall | Fix |
|---|---|
| "dubious ownership" on NTFS/FUSE mount | `git config --global --add safe.directory <path>` |
| Push fails with "Permission denied" | Token lacks repo scope; user must create a new token or use SSH |
| API repo creation returns 403 on fine-grained PAT | Token needs "Administration: Read and write" permission; or create repo manually at github.com/new |
| Fine-grained token scopes invisible | Check via `X-OAuth-Scopes` header — N/A means fine-grained. Edit permissions at github.com/settings/tokens |
| Cron job script path rejected | Use filename only, relative to `~/.hermes/scripts/` |
| SSH "Host key verification failed" | `ssh-keyscan github.com >> ~/.ssh/known_hosts` |
| Vault not found by obsidian skill | Check `OBSIDIAN_VAULT_PATH` in `~/.hermes/.env` is correct absolute path |
| Token output redacted in terminal | Hermes redacts `GITHUB_TOKEN=*** in terminal output. The actual value is in the file — use Python `open()` to read it programmatically. Piped commands (`grep | cut`) DO receive the real value. |
| Credential store not primed → cron push fails silently | Push once with tokenized URL, OR manually write to `~/.git-credentials`. Verify with clean-URL push after priming. |
| **Communicating time estimates to this user** | NEVER say "5 saniyelik iş", "2 dakika", or any time estimate. It reads as belittling. Just do the work without advertising how fast it'll be. |
| Disaster scenarios in examples | Never use "ev yanması" (house fire) or similar scenarios in examples — user finds them annoying. |
