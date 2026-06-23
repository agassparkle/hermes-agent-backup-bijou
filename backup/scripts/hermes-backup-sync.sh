#!/bin/bash
# Daily Hermes backup: config, skills, memories, cron → GitHub
set -e
BACKUP_DIR="$HOME/Hermes/hermes-agent-backup-bijou/backup"
HERMES_HOME="$HOME/.hermes"
REPO_DIR="$HOME/Hermes/hermes-agent-backup-bijou"
mkdir -p "$BACKUP_DIR"
cp "$HERMES_HOME/config.yaml" "$BACKUP_DIR/" 2>/dev/null || true
cp "$HERMES_HOME/context_length_cache.yaml" "$BACKUP_DIR/" 2>/dev/null || true
cp "$HERMES_HOME/gateway_state.json" "$BACKUP_DIR/" 2>/dev/null || true
cp "$HERMES_HOME/channel_directory.json" "$BACKUP_DIR/" 2>/dev/null || true
cp "$HERMES_HOME/SOUL.md" "$BACKUP_DIR/" 2>/dev/null || true
cp "$HERMES_HOME/memory_store.db" "$BACKUP_DIR/" 2>/dev/null || true
rm -rf "$BACKUP_DIR/skills" 2>/dev/null; cp -r "$HERMES_HOME/skills" "$BACKUP_DIR/" 2>/dev/null || true
rm -rf "$BACKUP_DIR/memories" 2>/dev/null; cp -r "$HERMES_HOME/memories" "$BACKUP_DIR/" 2>/dev/null || true
rm -rf "$BACKUP_DIR/cron" 2>/dev/null; cp -r "$HERMES_HOME/cron" "$BACKUP_DIR/" 2>/dev/null || true
cd "$REPO_DIR"
if [[ -z $(git status --porcelain) ]]; then exit 0; fi
git add -A
git commit -m "chore: backup hermes config, skills, memories ($(date '+%Y-%m-%d %H:%M'))" >/dev/null 2>&1
git push origin main 2>&1 | tail -1
echo "Hermes backup synced: $(date '+%Y-%m-%d %H:%M')"
