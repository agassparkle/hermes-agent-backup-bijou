#!/bin/bash
VAULT="/home/ubuntu/bijou-vault"
cd "$VAULT" || exit 1
if [[ -z $(git status --porcelain) ]]; then
    exit 0
fi
git add -A
git commit -m "auto-commit: $(date '+%Y-%m-%d %H:%M')" >/dev/null 2>&1
git push origin master 2>&1 | tail -1
echo "bijou-vault synced: $(date '+%Y-%m-%d %H:%M')"
