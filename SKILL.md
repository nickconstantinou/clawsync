---
name: clawback
description: Backup and restore your OpenClaw workspace to GitHub
metadata:
  {
    "openclaw": {
      "emoji": "💾",
      "requires": { "env": ["GITHUB_TOKEN"] }
    }
  }
---

# ClawBack

Backup and restore your OpenClaw workspace to GitHub.

## What It Backs Up

| Category | Description |
|----------|-------------|
| **Skills** | Custom skills in `$OPENCLAW_WORKSPACE/skills/` |
| **Scripts** | Automation scripts in `$OPENCLAW_WORKSPACE/scripts/` |
| **Identity Files** | AGENTS.md, SOUL.md, USER.md, MEMORY.md, TOOLS.md |

## What It Excludes

- ❌ API keys and tokens
- ❌ Credentials folder
- ❌ .env files
- ❌ node_modules
- ❌ Memory files
- ❌ Nested git repositories

## Environment Variables

```bash
export GITHUB_TOKEN="ghp_xxxx"
export BACKUP_REPO="username/repo-name"
export OPENCLAW_WORKSPACE="${HOME}/openclaw-workspace"
```

## Quick Start

```bash
# Clone
git clone https://github.com/your-username/clawback.git ~/clawback

# Configure
cp .env.example .env
# Edit .env with your values

# First backup
bash sync.sh
```

## Auth

Uses gh CLI if available, falls back to token auth.

## Files

- `sync.sh` - Backup script
- `restore.sh` - Restore script  
- `.env.example` - Template
- `.gitignore` - Blocks secrets
