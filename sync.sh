#!/bin/bash
# ClawSync - Secure Backup Script
# ShellCheck compliant: https://www.shellcheck.net/

set -euo pipefail

# === Pre-flight Check ===
REQUIRED_VARS=("BACKUP_REPO" "OPENCLAW_WORKSPACE")
for var in "${REQUIRED_VARS[@]}"; do
    if [[ -z "${!var}" ]]; then
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
# NOTE: SITES.md excluded - may contain API keys
WHITELIST=("AGENTS.md" "SOUL.md" "USER.md" "TOOLS.md" "IDENTITY.md" "HEARTBEAT.md")

for file in "${WHITELIST[@]}"; do
    if [[ -f "$WORKSPACE/$file" ]]; then
        cp "$WORKSPACE/$file" "$BACKUP_DIR/"
    fi
done

# === Safe Copy: Skills (with explicit deny list + find exclusion) ===
DENY_LIST=(".env" "credentials" "node_modules" "venv" "__pycache__")

if [[ -d "$WORKSPACE/skills" ]]; then
    rm -rf "$BACKUP_DIR/skills"
    mkdir -p "$BACKUP_DIR/skills"
    
    for skill in "$WORKSPACE/skills"/*; do
        if [[ ! -d "$skill" ]]; then
            continue
        fi
        
        # Check deny list
        skip=false
        for deny in "${DENY_LIST[@]}"; do
            if [[ "$skill" == *"$deny"* ]]; then
                skip=true
                break
            fi
        done
        
        if [[ "$skip" == false ]]; then
            # Use find to exclude .git directories
            find "$skill" -type d -name ".git" -prune -o -type f -print | while read -r f; do
                # shellcheck disable=SC2294
                cp -- "$f" "$BACKUP_DIR/skills/$(basename "$skill")/" 2>/dev/null || true
            done
            # Also copy directory structure
            cp -r "$skill" "$BACKUP_DIR/skills/" 2>/dev/null || true
        fi
    done
fi

# === Safe Copy: Scripts (with explicit deny list + find exclusion) ===
if [[ -d "$WORKSPACE/scripts" ]]; then
    rm -rf "$BACKUP_DIR/scripts"
    mkdir -p "$BACKUP_DIR/scripts"
    
    for script in "$WORKSPACE/scripts"/*; do
        if [[ ! -f "$script" ]]; then
            continue
        fi
        
        # Check deny list
        skip=false
        for deny in "${DENY_LIST[@]}"; do
            if [[ "$script" == *"$deny"* ]]; then
                skip=true
                break
            fi
        done
        
        # Also skip .git directories
        if [[ "$script" == *".git"* ]]; then
            skip=true
        fi
        
        if [[ "$skip" == false ]]; then
            cp -r "$script" "$BACKUP_DIR/scripts/"
        fi
    done
fi

echo "Files copied"

cd "$BACKUP_DIR"
if [[ ! -d ".git" ]]; then
    git init
    git remote add origin "https://github.com/${BACKUP_REPO}.git"
fi

# === Secret Detection (Pre-Commit Check) ===
# Comprehensive regex for secrets detection
SECRET_PATTERN='(ghp_[a-zA-Z0-9]{36}|sk-[a-zA-Z0-9]{20,}|AIza[a-zA-Z0-9_-]{35}|xox[pborsa]-[0-9a-zA-Z]{10,48}|AKIA[0-9A-Z]{16}|[a-zA-Z0-9/+=]{40,}|(-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----))'

# Scan all staged files for secrets
if git diff --cached --name-only | xargs -I {} grep -qE "$SECRET_PATTERN" {} 2>/dev/null; then
    echo "Error: Potential API key or secret detected in staged files. Aborting."
    echo "Please review the following files and remove any secrets:"
    git diff --cached --name-only | xargs -I {} grep -lE "$SECRET_PATTERN" {} 2>/dev/null || true
    git reset
    exit 1
fi

# === Git Push ===
if gh auth status &>/dev/null; then
    GIT_CMD="git"
    gh auth setup-git
else
    if [[ -z "$TOKEN" ]]; then
        echo "Error: No GH auth or GITHUB_TOKEN"
        exit 1
    fi
    GIT_CMD="git -c http.extraHeader=\"Authorization: bearer ${TOKEN}\""
fi

if ! git diff --cached --quiet; then
    git commit -m "Backup: $(date '+%Y-%m-%d %H:%M')"
    # shellcheck disable=SC2086
    eval "$GIT_CMD push -u origin $BRANCH"
    echo "Backup complete!"
fi
