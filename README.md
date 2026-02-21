# ClawBack

Backup and restore your OpenClaw workspace to GitHub.

## Quick Start

```bash
git clone https://github.com/your-username/clawback.git ~/clawback
cp .env.example .env
# Edit .env with your values
bash sync.sh
```

## Auth

Uses gh CLI if available, falls back to token auth.

## Files

- `sync.sh` - Backup
- `restore.sh` - Restore
- `.env.example` - Template
