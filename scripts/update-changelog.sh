#!/bin/bash
cd /home/openclaw/openclaw-workspace
TODAY=$(date +%Y-%m-%d)
echo "## $TODAY" >> CHANGELOG.md
git log --since="00:00" --oneline >> CHANGELOG.md 2>/dev/null
