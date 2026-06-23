---
name: hermes-backup-restore
description: "Backup and restore Hermes config, skills, memories, and holographic memory to/from GitHub."
version: 1.0.0
author: Hermes Agent
tags: [hermes, backup, restore, github]
---

# Hermes Backup & Restore

## Backup Repository
`https://github.com/agassparkle/hermes-agent-backup-wacu`
Local clone: `~/Hermes/hermes-agent-backup-wacu/`
Backup destination: `~/Hermes/hermes-agent-backup-wacu/backup/`

## What Is Backed Up
- `config.yaml` — main Hermes config
- `context_length_cache.yaml`
- `gateway_state.json` — gateway routing state
- `channel_directory.json` — platform channel mapping
- `SOUL.md` — personality file
- `skills/` — all installed skills
- `memories/` — MEMORY.md and USER.md
- `cron/` — scheduled jobs
- `memory_store.db` — holographic fact store (fact_store)
- `home-server/` — server inventory notes

## What Is NOT Backed Up (secrets — never commit)
- `~/.hermes/.env` (API keys, tokens)
- Home Assistant token
- OAuth credentials (`auth.json`)
- Session history (`state.db`)

---

## Running a Backup

```python
import shutil, os

BACKUP_DIR = os.path.expanduser("~/Hermes/hermes-agent-backup-wacu/backup")
HERMES_HOME = os.path.expanduser("~/.hermes")

items = [
    ("config.yaml", False),
    ("context_length_cache.yaml", False),
    ("gateway_state.json", False),
    ("channel_directory.json", False),
    ("SOUL.md", False),
    ("memory_store.db", False),
    ("skills", True),
    ("memories", True),
    ("cron", True),
]

for name, is_dir in items:
    src = os.path.join(HERMES_HOME, name)
    dst = os.path.join(BACKUP_DIR, name)
    if not os.path.exists(src):
        continue
    if is_dir:
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)
```

Then commit and push:
```bash
cd ~/Hermes/hermes-agent-backup-wacu
git add -A
git commit -m "chore: backup hermes config, skills, and memories"
git push
```

---

## Restoring from Backup

### 1. Clone repo (if needed)
```bash
git clone https://github.com/agassparkle/hermes-agent-backup-wacu.git ~/Hermes/hermes-agent-backup-wacu
```

### 2. Stop gateway
```bash
hermes gateway stop
```

### 3. Copy files back
```bash
BACKUP=~/Hermes/hermes-agent-backup-wacu/backup

cp $BACKUP/config.yaml ~/.hermes/
cp $BACKUP/memory_store.db ~/.hermes/
cp $BACKUP/gateway_state.json ~/.hermes/
cp $BACKUP/channel_directory.json ~/.hermes/
cp $BACKUP/SOUL.md ~/.hermes/
cp -r $BACKUP/skills ~/.hermes/
cp -r $BACKUP/memories ~/.hermes/
cp -r $BACKUP/cron ~/.hermes/
```

### 4. Re-add secrets (not in backup)
- API keys → `~/.hermes/.env`
- Home Assistant token → add to `.env` or re-paste when prompted
- OAuth credentials → `hermes auth add <provider>`

### 5. Restart gateway
```bash
hermes gateway start
```

---

## Pitfalls
- Never commit `~/.hermes/.env` — it contains API keys
- `state.db` (session history) is large and not backed up
- After restore, run `hermes doctor` to verify everything is healthy
