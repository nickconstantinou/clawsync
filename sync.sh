#!/bin/bash
# ClawSync - Secure Backup Script

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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${SCRIPT_DIR}"

echo "=== ClawSync Backup ==="

# === Strict Whitelist: Identity Files ===
WHITELIST=("AGENTS.md" "SOUL.md" "USER.md" "TOOLS.md" "IDENTITY.md" "SITES.md" "HEARTBEAT.md")

for file in "${WHITELIST[@]}"; do
    if [ -f "$WORKSPACE/$file" ]; then
        cp "$WORKSPACE/$file" "$BACKUP_DIR/"
    fi
done

# === Safe Copy: Skills (with deny list) ===
DENY_LIST=(".env" "credentials" ".git" "node_modules" "venv" "__pycache__")

if [ -d "$WORKSPACE/skills" ]; then
    rm -rf "$BACKUP_DIR/skills"
    mkdir -p "$BACKUP_DIR/skills"
    
    for skill in "$WORKSPACE/skills"/*; do
        [ -d "$skill" ] || continue
        
        # Check deny list
        skip=false
        for deny in "${DENY_LIST[@]}"; do
            if [ "$skill" == *"${deny}" ]; then
                skip=true
                break
            fi
        done
        
        [ "$skip" = false ] && cp -r "$skill" "$BACKUP_DIR/skills/"
    done
fi

# === Safe Copy: Scripts (with deny list) ===
if [ -d "$WORKSPACE/scripts" ]; then
    rm -rf "$BACKUP_DIR/scripts"
    mkdir -p "$BACKUP_DIR/scripts"
    
    for script in "$WORKSPACE/scripts"/*; do
        [ -f "$script" ] || continue
        
        # Check deny list
        skip=false
        for deny in "${DENY_LIST[@]}"; do
            if [ "$script" == *"${deny}" ]; then
                skip=true
                break
            fi
        done
        
        [ "$skip" = false ] && cp -r "$script" "$BACKUP_DIR/scripts/"
    done
fi

echo "Files copied"

cd "$BACKUP_DIR"
[ ! -d ".git" ] && git init && git remote add origin "https://github.com/${BACKUP_REPO}.git"
git add -A

# === Secret Scrubbing ===
if git diff --cached | grep -qE "(ghp_[a-zA-Z0-9]{36}|sk-[a-zA-Z0-9]{20,}|AIza[a-zA-Z0-9_-]{35})"; then
    echo "Error: Potential API key detected in staged files. Aborting push."
    exit 1
fi

# === Git Push ===
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
