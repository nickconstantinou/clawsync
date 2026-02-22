---
name: gemini
description: Use Google Gemini for AI tasks
metadata:
  {
    "openclaw": {
      "emoji": "🔮",
      "requires": { "env": ["GEMINI_API_KEY"] }
    }
  }
---

# Gemini Skill

Use Google Gemini for AI tasks.

## Credentials

Stored in `~/.openclaw/.env`:

```
GEMINI_API_KEY=AIzaSy...
```

## Usage

```bash
source ~/.openclaw/.env
echo $GEMINI_API_KEY
```

## Model Selection

**Always use:**
- `gemini-3-flash` - Best for everything
- `gemini-2.5-flash` - Fallback

**Deprecated:**
- gemini-1.5-flash
- gemini-2.0-flash
