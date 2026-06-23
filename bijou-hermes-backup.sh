#!/bin/bash
set -e
REPO_DIR="$HOME/Hermes/hermes-agent-backup-bijou"
BACKUP_DIR="$REPO_DIR/backup"
HERMES_DIR="$HOME/.hermes"
rm -rf "$BACKUP_DIR"
cp -a "$HERMES_DIR" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR/audio_cache" "$BACKUP_DIR/cache" "$BACKUP_DIR/sessions" \
       "$BACKUP_DIR/lsp" "$BACKUP_DIR/node" "$BACKUP_DIR/bin" \
       "$BACKUP_DIR/hermes-agent" \
       "$BACKUP_DIR/.env" "$BACKUP_DIR/auth.json" \
       "$BACKUP_DIR/google_token.json" "$BACKUP_DIR/google_client_secret.json" 2>/dev/null || true
cd "$REPO_DIR"
git add -A .
git commit -m "backup: $(date "+%Y-%m-%d %H:%M:%S")" || true
git push origin main
