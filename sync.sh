#!/bin/bash
# ClawBack Sync - Backup OpenClaw workspace to GitHub

# === Configuration ===
WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/openclaw-workspace}"
BACKUP_REPO="${BACKUP_REPO:-}"
BRANCH="${BACKUP_BRANCH:-main}"
TOKEN="${GITHUB_TOKEN:-}"

# === Try gh auth first ===
use_gh_auth() {
    if gh auth status &>/dev/null; then
        gh auth setup-git
        return 0
    fi
    return 1
}

# === Fallback: use http.extraHeader ===
use_token_auth() {
    if [ -z "$TOKEN" ]; then
        echo "Error: GITHUB_TOKEN not set"
        exit 1
    fi
    git remote set-url origin "https://github.com/${BACKUP_REPO}.git"
    git config http.extraHeader "Authorization: bearer ${TOKEN}"
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${SCRIPT_DIR}"

echo "=== ClawBack Sync ==="

# Try gh auth, fallback to token
if ! use_gh_auth; then
    echo "gh not authenticated, using token auth"
    use_token_auth
fi

# Copy files
for file in AGENTS.md SOUL.md USER.md MEMORY.md TOOLS.md IDENTITY.md SITES.md HEARTBEAT.md; do
    [ -f "$WORKSPACE/$file" ] && cp "$WORKSPACE/$file" "$BACKUP_DIR/" 2>/dev/null || true
done

[ -d "$WORKSPACE/skills" ] && {
    rm -rf "$BACKUP_DIR/skills"
    mkdir -p "$BACKUP_DIR/skills"
    for skill in "$WORKSPACE/skills"/*; do
        [ -d "$skill" ] && [ ! -d "$skill/.git" ] && cp -r "$skill" "$BACKUP_DIR/skills/"
    done
}

[ -d "$WORKSPACE/scripts" ] && {
    rm -rf "$BACKUP_DIR/scripts"
    mkdir -p "$BACKUP_DIR/scripts"
    cp -r "$WORKSPACE/scripts/"* "$BACKUP_DIR/scripts/" 2>/dev/null || true
}

echo "Files copied"

cd "$BACKUP_DIR"
[ ! -d ".git" ] && git init
git add -A
git diff --cached --quiet || {
    git commit -m "Backup: $(date '+%Y-%m-%d %H:%M')"
    git push -u origin "$BRANCH"
    echo "Backup complete!"
}
