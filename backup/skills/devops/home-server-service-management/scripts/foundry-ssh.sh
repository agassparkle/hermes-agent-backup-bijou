#!/usr/bin/env bash
# foundry-ssh.sh — connect to the user's Oracle Cloud "foundry" server.
# Usage: ./foundry-ssh.sh [command...]
#   With no args: opens interactive shell.
#   With args:     runs the quoted command on foundry.
#
# All connection details (key path, user, host) come from the user's
# home-server-service-management skill — keep them in sync if they change.

set -euo pipefail

KEY="/mnt/sda2/UBuntu_Backup/Oracle Cloud  Keys/agassparkle.key"
HOST="ubuntu@141.144.205.247"
SSH_OPTS=(
  -i "$KEY"
  -o BatchMode=yes
  -o StrictHostKeyChecking=accept-new
)

if [[ $# -eq 0 ]]; then
  exec ssh "${SSH_OPTS[@]}" "$HOST"
else
  exec ssh "${SSH_OPTS[@]}" "$HOST" "$@"
fi
