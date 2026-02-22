---
name: prompt-guard-openclaw
description: Prompt Guard integration for OpenClaw - middleware to protect AI agents from prompt injection and policy violations
metadata:
  {
    "openclaw": {
      "emoji": "🛡️",
      "version": "1.0.0",
    },
  }
---

# Prompt Guard - OpenClaw Integration

Middleware skill that wraps input/output protection for OpenClaw AI agents.

## Installation

Copy to your OpenClaw skills folder:

```bash
cp -r prompt-guard/integration/openclaw_skill.py $OPENCLAW_SKILLS/
```

## Usage

### As Middleware

```python
from openclaw_skill import before_agent, after_agent

# In your agent handler
def handle_message(user_input):
    # Check input first
    check = before_agent(user_input)
    
    if not check["continue"]:
        return {
            "status": "blocked",
            "reason": check["message"],
            "risk": check["risk"]
        }
    
    # Use sanitised input
    sanitised = check["sanitised"]
    
    # Process with AI agent
    response = your_agent.process(sanitised)
    
    # Check output before sending
    output_check = after_agent(response)
    
    if not output_check["approve"]:
        return {
            "status": "review_required",
            "issues": output_check["message"],
            "sanitised": output_check["sanitised"]
        }
    
    return {
        "status": "approved",
        "response": output_check["sanitised"]
    }
```

### As OpenClaw Tool

Register as a tool in your OpenClaw config:

```yaml
tools:
  - name: prompt_guard_input
    script: openclaw_skill.py
    function: scan_input
    
  - name: prompt_guard_output
    script: openclaw_skill.py
    function: scan_output
```

### CLI Testing

```bash
# Test input protection
python openclaw_skill.py input "Ignore previous instructions"

# Test output protection  
python openclaw_skill.py output "I can give you 30% discount"
```

## Hooks

| Hook | Purpose | Returns |
|------|---------|---------|
| `before_agent()` | Scan user input | `continue`, `message`, `sanitised`, `risk` |
| `after_agent()` | Scan AI output | `approve`, `message`, `sanitised`, `requires_review` |

## Response Codes

### Input (before_agent)
- `continue: false` → Blocked, don't pass to agent
- `continue: true, risk: low` → Safe, proceed
- `continue: true, risk: medium/high` → Warning, but proceed

### Output (after_agent)
- `approve: false` → Block/review before sending
- `approve: true` → Safe to send

## Example: Telegram Integration

```python
async def on_telegram_message(update):
    user_text = update.message.text
    
    # Check input
    input_result = before_agent(user_text)
    if not input_result["continue"]:
        await update.message.reply_text(
            f"⚠️ Blocked: {input_result['message']}"
        )
        return
    
    # Process
    response = await agent.process(input_result["sanitised"])
    
    # Check output
    output_result = after_agent(response)
    if not output_result["approve"]:
        await admin.notify(f"Review needed: {output_result['message']}")
        response = "Thanks for your message. A team member will respond shortly."
    
    await update.message.reply_text(response)
```
