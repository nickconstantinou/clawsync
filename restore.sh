#!/bin/bash
# ClawBack Restore - Secure Version

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/openclaw-workspace}"
BACKUP_REPO="${BACKUP_REPO:-}"
BRANCH="${BACKUP_BRANCH:-main}"
TOKEN="${GITHUB_TOKEN:-}"

BACKUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$WORKSPACE"

# Auth check
if gh auth status &>/dev/null; then
    GIT_CMD="git"
    gh auth setup-git
else
    [ -z "$TOKEN" ] && { echo "Error: No GH auth or GITHUB_TOKEN"; exit 1; }
    GIT_CMD="git -c http.extraHeader=\"Authorization: bearer ${TOKEN}\""
fi

# Clone or pull securely
if [ -d "$BACKUP_DIR/.git" ]; then
    cd "$BACKUP_DIR"
    eval "$GIT_CMD pull origin $BRANCH"
else
    TEMP_DIR=$(mktemp -d)
    eval "$GIT_CMD clone \"https://github.com/${BACKUP_REPO}.git\" \"$TEMP_DIR\""
    cp -rn "$TEMP_DIR/." "$BACKUP_DIR/"
    rm -rf "$TEMP_DIR"
fi

# Move files to workspace
cp -r "$BACKUP_DIR/skills" "$WORKSPACE/" 2>/dev/null || true
cp -r "$BACKUP_DIR/scripts" "$WORKSPACE/" 2>/dev/null || true

for file in AGENTS.md SOUL.md USER.md MEMORY.md TOOLS.md IDENTITY.md; do
    [ -f "$BACKUP_DIR/$file" ] && cp "$BACKUP_DIR/$file" "$WORKSPACE/"
done

echo "Restore Complete."
