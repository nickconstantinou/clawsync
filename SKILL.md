---
name: clawback
description: Backup and restore your OpenClaw workspace to GitHub
metadata:
  {
    "openclaw": {
      "emoji": "💾",
      "requires": { 
        "env": ["GITHUB_TOKEN", "BACKUP_REPO", "OPENCLAW_WORKSPACE"] 
      }
    }
  }
---

# ClawSync

Backup and restore your OpenClaw workspace to GitHub.

## What It Backs Up

| Category | Description |
|----------|-------------|
| **Skills** | Custom skills in `$OPENCLAW_WORKSPACE/skills/` |
| **Scripts** | Automation scripts in `$OPENCLAW_WORKSPACE/scripts/` |
| **Identity Files** | AGENTS.md, SOUL.md, USER.md, MEMORY.md, TOOLS.md, IDENTITY.md, SITES.md, HEARTBEAT.md |

## What It Excludes

- ❌ API keys and tokens
- ❌ Credentials folder
- ❌ .env files
- ❌ node_modules
- ❌ .git directories
- ❌ Nested git repositories

## Environment Variables (Required)

```bash
export GITHUB_TOKEN="ghp_xxxx"
export BACKUP_REPO="username/repo-name"
export OPENCLAW_WORKSPACE="${HOME}/openclaw-workspace"
```

## Quick Start

```bash
git clone https://github.com/your-username/clawsync.git ~/clawsync
cp .env.example .env
# Edit .env with your values
bash sync.sh
```

## Features

- **Pre-flight Check**: Validates required env vars before running
- **Strict Whitelist**: Only copies explicitly allowed files
- **Deny List**: Filters out .git, credentials, node_modules
- **Secret Scrubbing**: Detects API keys and aborts push
- **Safe Restore**: Requires --force or confirmation before overwriting

## Safe Restore

```bash
# With confirmation (default)
bash restore.sh

# Force mode (no prompt)
bash restore.sh --force
```

## Auth

Uses gh CLI if available, falls back to token auth.

## Files

- `sync.sh` - Backup script
- `restore.sh` - Restore script  
- `.env.example` - Template
- `.gitignore` - Blocks secrets
