#!/bin/bash
# ClawSync - Secure Restore Script

# === Pre-flight Check ===
REQUIRED_VARS=("BACKUP_REPO" "OPENCLAW_WORKSPACE")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Error: $var is not set. Please configure in .env"
        exit 1
    fi
done

WORKSPACE="${OPENCLAW_WORKSPACE}"
BACKUP_REPO="${BACKUP_REPO}"
BRANCH="${BACKUP_BRANCH:-main}"
TOKEN="${GITHUB_TOKEN:-}"
FORCE="${1:-}"

BACKUP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$WORKSPACE"

echo "=== ClawSync Restore ==="

# === Safe Restore: Require --force or confirmation ===
if [ "$FORCE" != "--force" ] && [ "$FORCE" != "-f" ]; then
    echo "Warning: This will overwrite existing files in $WORKSPACE"
    echo "Are you sure? (y/n)"
    read -r response
    if [ "$response" != "y" ] && [ "$response" != "Y" ]; then
        echo "Restore cancelled."
        exit 0
    fi
fi

# === Auth ===
if gh auth status &>/dev/null; then
    GIT_CMD="git"
    gh auth setup-git
else
    [ -z "$TOKEN" ] && { echo "Error: No GH auth or GITHUB_TOKEN"; exit 1; }
    GIT_CMD="git -c http.extraHeader=\"Authorization: bearer ${TOKEN}\""
fi

# === Clone or Pull ===
if [ -d "$BACKUP_DIR/.git" ]; then
    cd "$BACKUP_DIR"
    eval "$GIT_CMD pull origin $BRANCH"
else
    TEMP_DIR=$(mktemp -d)
    eval "$GIT_CMD clone \"https://github.com/${BACKUP_REPO}.git\" \"$TEMP_DIR\""
    cp -rn "$TEMP_DIR/." "$BACKUP_DIR/"
    rm -rf "$TEMP_DIR"
fi

# === Restore Files (no-clobber by default) ===
[ -d "$BACKUP_DIR/skills" ] && cp -rn "$BACKUP_DIR/skills"/* "$WORKSPACE/skills/" 2>/dev/null || mkdir -p "$WORKSPACE/skills" && cp -rn "$BACKUP_DIR/skills/"* "$WORKSPACE/skills/"
[ -d "$BACKUP_DIR/scripts" ] && cp -rn "$BACKUP_DIR/scripts"/* "$WORKSPACE/scripts/" 2>/dev/null || mkdir -p "$WORKSPACE/scripts" && cp -rn "$BACKUP_DIR/scripts/"* "$WORKSPACE/scripts/"

for file in AGENTS.md SOUL.md USER.md MEMORY.md TOOLS.md IDENTITY.md SITES.md HEARTBEAT.md; do
    [ -f "$BACKUP_DIR/$file" ] && cp -n "$BACKUP_DIR/$file" "$WORKSPACE/" 2>/dev/null || true
done

echo "Restore complete!"
