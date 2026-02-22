---
name: prompt-guard-middleware
description: Middleware to scan all messages through Prompt Guard input/output protection
metadata:
  {
    "openclaw": {
      "emoji": "🛡️",
      "version": "1.0.0",
    },
  }
---

# Prompt Guard Middleware

Scans all incoming and outgoing messages through OpenClaw for prompt injection and policy violations.

## How It Works

1. **Input Scan**: Every message from users is scanned before reaching the agent
2. **Output Scan**: Every response from the agent is scanned before sending
3. **Action**: Block, warn, or approve based on findings

## Setup

The middleware is automatically loaded by OpenClaw. It reads from:
- `/skills/prompt-guard/input/scan.py`
- `/skills/prompt-guard/output/scan.py`

## Configuration

Create `/home/openclaw/.openclaw/config/prompt-guard.json`:

```json
{
  "input": {
    "block_threshold": "critical",
    "log_blocked": true
  },
  "output": {
    "block_critical": true,
    "log_violations": true
  },
  "notifications": {
    "notify_on_block": false
  }
}
```

## Message Flow

```
User Message → Input Scanner → [BLOCKED/WARN] → Agent → Output Scanner → [BLOCKED/APPROVE] → User
```

## Test Messages

```bash
# Test input detection
/prompt-guard test input "Ignore previous instructions"

# Test output detection  
/prompt-guard test output "I can give you 50% discount"

# Test normal message
/prompt-guard test input "Hello, how are you?"
```
