#!/bin/bash
# ClawBack Restore - Restore OpenClaw workspace from backup

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/openclaw-workspace}"
BACKUP_REPO="${BACKUP_REPO:-}"
BRANCH="${BACKUP_BRANCH:-main}"
TOKEN="${GITHUB_TOKEN:-}"

use_gh_auth() {
    if gh auth status &>/dev/null; then
        gh auth setup-git
        return 0
    fi
    return 1
}

use_token_auth() {
    [ -z "$TOKEN" ] && exit 1
    git remote set-url origin "https://github.com/${BACKUP_REPO}.git"
    git config http.extraHeader "Authorization: bearer ${TOKEN}"
}

echo "=== ClawBack Restore ==="
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$SCRIPT_DIR"
mkdir -p "$WORKSPACE"

# Clone or pull
if [ -d "$BACKUP_DIR/.git" ]; then
    cd "$BACKUP_DIR"
    use_gh_auth || use_token_auth
    git pull origin "$BRANCH" 2>/dev/null || true
else
    use_gh_auth || use_token_auth
    git clone "https://github.com/${BACKUP_REPO}.git" "$BACKUP_DIR"
    cd "$BACKUP_DIR"
fi

# Restore files
for file in AGENTS.md SOUL.md USER.md MEMORY.md TOOLS.md IDENTITY.md SITES.md HEARTBEAT.md; do
    [ -f "$BACKUP_DIR/$file" ] && cp "$BACKUP_DIR/$file" "$WORKSPACE/"
done

[ -d "$BACKUP_DIR/skills" ] && mkdir -p "$WORKSPACE/skills" && cp -r "$BACKUP_DIR/skills/"* "$WORKSPACE/skills/"
[ -d "$BACKUP_DIR/scripts" ] && mkdir -p "$WORKSPACE/scripts" && cp -r "$BACKUP_DIR/scripts/"* "$WORKSPACE/scripts/"

echo "=== Restore Complete ==="
echo "Files restored to: $WORKSPACE"
