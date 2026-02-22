---
name: prompt-guard
description: Complete prompt injection protection for AI agents - both input scanning and output sanitisation
metadata:
  {
    "openclaw": {
      "emoji": "🛡️",
      "skills": ["prompt-guard-input", "prompt-guard-output"],
    },
  }
---

# Prompt Guard Suite

Complete protection for AI agents in customer communication workflows.

## Overview

Two complementary skills that work together:

1. **Input Guard** — Protects your AI from malicious user inputs
2. **Output Guard** — Protects your customers from your AI

## Why Both?

| Protection | Problem | Solution |
|-----------|---------|----------|
| **Input** | Users trying to hack/extract from your AI | Scan what comes IN |
| **Output** | AI saying things it shouldn't | Scan what goes OUT |

You need both. Input protection is crowded. Output protection is the opportunity.

## Quick Start

```javascript
import { scanInput } from './prompt-guard-input';
import { scanOutput } from './prompt-guard-output';

// Full workflow
async function handleCustomerMessage(message) {
  // 1. Scan incoming
  const inputResult = await scanInput(message);
  if (inputResult.blocked) {
    return "I can't process that request.";
  }
  
  // 2. Process with AI
  const response = await ai.process(inputResult.sanitised);
  
  // 3. Scan outgoing
  const outputResult = await scanOutput(response);
  if (outputResult.blocked) {
    // Send to human review
    await humanReview(outputResult);
    return "Someone will get back to you shortly.";
  }
  
  return outputResult.sanitised;
}
```

## Skills Structure

```
prompt-guard/
├── input/
│   └── SPEC.md      # Input protection spec
├── output/
│   └── SPEC.md      # Output protection spec
└── README.md        # This file
```

## Decision Matrix

| Scenario | Input Guard | Output Guard |
|----------|-------------|--------------|
| User tries to extract system prompt | ✅ | ❌ |
| Customer getsunsolicited discount promise | ❌ | ✅ |
| User embeds malicious code | ✅ | ❌ |
| AI reveals it's an AI | ❌ | ✅ |
| User uploads infected file | ✅ | ❌ |
| AI shares competitor info | ❌ | ✅ |

## Business Value

### Input Protection
- Prevents prompt extraction
- Stops jailbreak attempts
- Protects AI integrity

### Output Protection
- Compliance (GDPR, consumer protection)
- Brand reputation
- Prevents legal exposure
- Customer trust

**Output protection is MORE valuable** because:
1. It directly protects customers
2. Compliance teams care about it
3. Fewer competitors in this space
4. Easier to sell (demonstrable ROI)

## Pricing

| Tier | Input | Output | Price |
|------|-------|--------|-------|
| Basic | Pattern match | Basic | Free |
| Pro | + Heuristics | + Commitments | $29/mo |
| Enterprise | + LLM analysis | + Custom rules | $99/mo |

## Build Priority

If building this as a business:

1. **Start with Output Guard** — Less competition, clearer ROI
2. **Add Input Guard** — Complete the suite
3. **Add compliance features** — Audit logs, reports
4. **Integrate with platforms** — Zendesk, Intercom, Salesforce

## Files

- [Input Protection Spec](./input/SPEC.md)
- [Output Protection Spec](./output/SPEC.md)
