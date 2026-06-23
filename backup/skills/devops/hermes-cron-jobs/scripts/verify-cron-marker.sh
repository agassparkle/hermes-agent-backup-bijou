#!/bin/bash
# verify-cron-marker.sh — Quick marker file check for cron jobs
# Usage: ./verify-cron-marker.sh <job-name>
# Example: ./verify-cron-marker.sh pill-reminder-test

set -euo pipefail

JOB_NAME="${1:-}"
if [[ -z "$JOB_NAME" ]]; then
    echo "Usage: $0 <job-name>"
    echo "Example: $0 pill-reminder-test"
    exit 1
fi

MARKER_PATTERN="/tmp/${JOB_NAME}-$(date +%F).marker"

echo "Checking marker: $MARKER_PATTERN"
echo "Today: $(date +%F)"
echo ""

if [[ -f "$MARKER_PATTERN" ]]; then
    echo "✅ MARKER EXISTS — job already ran today"
    echo "File: $MARKER_PATTERN"
    ls -la "$MARKER_PATTERN"
    echo ""
    echo "Contents (if any):"
    cat "$MARKER_PATTERN" 2>/dev/null || echo "(empty)"
    exit 0
else
    echo "❌ NO MARKER — job has NOT run today (or marker expired)"
    echo ""
    echo "All markers for this job:"
    ls -la /tmp/${JOB_NAME}-*.marker 2>/dev/null || echo "  (none)"
    exit 1
fi