#!/bin/bash
# Test sync.sh - verifies backup functionality
# Exit codes: 0 = pass, 1 = fail

set -euo pipefail

SCRIPT_DIR="/home/openclaw/.openclaw/workspace/projects/clawsync/scripts"
REPO_DIR="/home/openclaw/.openclaw/workspace/projects/clawsync"

# Create temp directories
WORKSPACE_DIR="/tmp/clawsync-test-workspace"
BACKUP_DIR="/tmp/clawsync-test-backup"

# Cleanup
rm -rf "$WORKSPACE_DIR" "$BACKUP_DIR" 2>/dev/null || true

# Set up test workspace
mkdir -p "$WORKSPACE_DIR/skills" "$WORKSPACE_DIR/scripts"

# Personal files that should NOT be copied
echo "personal" > "$WORKSPACE_DIR/AGENTS.md"
echo "personal" > "$WORKSPACE_DIR/USER.md"
echo "personal" > "$WORKSPACE_DIR/SOUL.md"

# Test files that SHOULD be copied
echo "echo test" > "$WORKSPACE_DIR/scripts/test.sh"
mkdir -p "$WORKSPACE_DIR/skills/test-skill"
echo "# Test Skill" > "$WORKSPACE_DIR/skills/test-skill/SKILL.md"

# Run sync.sh (it will use BACKUP_DIR as its working dir)
mkdir -p "$BACKUP_DIR"
cd "$BACKUP_DIR"
cp "$REPO_DIR/sync.sh" .
cp "$REPO_DIR/restore.sh" .

export BACKUP_REPO="test/repo"
export OPENCLAW_WORKSPACE="$WORKSPACE_DIR"
export GITHUB_TOKEN="dummy"

# Run sync (ignore push failure - expected with dummy token)
bash sync.sh || true

# Verify personal files NOT copied
check_not_copied() {
    local file="$1"
    if [[ -f "$BACKUP_DIR/$file" ]]; then
        echo "FAIL: $file should NOT have been copied"
        exit 1
    fi
}

check_not_copied "AGENTS.md"
check_not_copied "USER.md"
check_not_copied "SOUL.md"
check_not_copied "TOOLS.md"
check_not_copied "IDENTITY.md"
check_not_copied "HEARTBEAT.md"
check_not_copied "SITES.md"

# Verify test files WERE copied
check_copied() {
    local file="$1"
    if [[ ! -f "$BACKUP_DIR/$file" ]]; then
        echo "FAIL: $file should have been copied"
        exit 1
    fi
}

check_copied "scripts/test.sh"
check_copied "skills/test-skill/SKILL.md"

echo "✅ sync.sh test passed"
exit 0
