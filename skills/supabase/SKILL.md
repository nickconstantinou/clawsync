---
name: supabase
description: Manage Supabase database for ExamPulse and UK Tutors Directory
metadata:
  {
    "openclaw": {
      "emoji": "🗄️",
      "requires": { "env": ["SUPABASE_REF", "SUPABASE_SERVICE_KEY"] }
    }
  }
---

# Supabase Skill

Manage Supabase database.

## Credentials

Credentials are stored in `~/.openclaw/.env`:

```
SUPABASE_REF=araqigsimkjsmwhnjesv
SUPABASE_URL=https://araqigsimkjsmwhnjesvSUPABASE_SERVICE_KEY=sbp_...
```

## Usage

### Set.supabase.co
 credentials:

```bash
source ~/.openclaw/.env
export SUPABASE_SERVICE_KEY="$SUPABASE_SERVICE_KEY"
```

### Access URL:

```bash
source ~/.openclaw/.env
echo $SUPABASE_URL
```

## Projects

- **exam-pulse-marketing**: `araqigsimkjsmwhnjesv`
- **UK Tutors Directory**: Uses public data (no DB)

## Important

- **NEVER hardcode keys** - Always use `.env`
- Use **service role key** for admin operations (stored in `.env`)
- Use **anon key** for frontend (public-safe)
