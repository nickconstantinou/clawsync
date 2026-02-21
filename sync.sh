#!/bin/bash
# ClawBack Sync - Secure Version

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/openclaw-workspace}"
BACKUP_REPO="${BACKUP_REPO:-}"
BRANCH="${BACKUP_BRANCH:-main}"
TOKEN="${GITHUB_TOKEN:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${SCRIPT_DIR}"

# Copy Identity files
for file in AGENTS.md SOUL.md USER.md MEMORY.md TOOLS.md IDENTITY.md SITES.md HEARTBEAT.md; do
    [ -f "$WORKSPACE/$file" ] && cp "$WORKSPACE/$file" "$BACKUP_DIR/" 2>/dev/null || true
done

# Copy Skills & Scripts
[ -d "$WORKSPACE/skills" ] && cp -r "$WORKSPACE/skills" "$BACKUP_DIR/"
[ -d "$WORKSPACE/scripts" ] && cp -r "$WORKSPACE/scripts" "$BACKUP_DIR/"

cd "$BACKUP_DIR"
[ ! -d ".git" ] && git init && git remote add origin "https://github.com/${BACKUP_REPO}.git"
git add -A

# Define the secure git command
if gh auth status &>/dev/null; then
    GIT_CMD="git"
    gh auth setup-git
else
    [ -z "$TOKEN" ] && { echo "Error: No GH auth or GITHUB_TOKEN"; exit 1; }
    GIT_CMD="git -c http.extraHeader=\"Authorization: bearer ${TOKEN}\""
fi

if ! git diff --cached --quiet; then
    git commit -m "Backup: $(date '+%Y-%m-%d %H:%M')"
    eval "$GIT_CMD push -u origin $BRANCH"
    echo "Backup complete!"
fi
