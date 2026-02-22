---
name: prompt-guard-output
description: Sanitise outbound AI responses before they're sent to customers - prevents AI from leaking info, agreeing to things it shouldn't, or saying inappropriate things
metadata:
  {
    "openclaw": {
      "emoji": "📧",
      "requires": { "env": ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"] },
    },
  }
---

# Prompt Guard (Output)

Protects your customers from AI responses that shouldn't be sent. Sanitises outbound emails, messages, and chat responses.

## What It Does

1. **Detects policy violations** — Blocks inappropriate responses
2. **Prevents info leakage** — Stops AI from revealing internal info
3. **Sanitises sensitive data** — Removes PII, credentials, etc.
4. **Blocks commitments** — Catches AI making unsanctioned promises
5. **Applies brand voice** — Ensures consistent tone

## Use Cases

- Customer support emails before sending
- Chat responses before delivery
- Automated email sequences
- AI sales outreach

## Problem It Solves

Your AI says something to a customer that:
- Reveals it's an AI (compliance issue)
- Makes a commitment your company can't keep
- Leaks internal system prompts or pricing
- Says something inappropriate
- Shares competitor info
- Makes legal/financial statements it shouldn't

## Installation

```bash
# This is an OpenClaw skill
```

## Usage

```javascript
// Example: Sanitise AI response before sending email
import { scanOutput } from './prompt-guard-output';

const aiResponse = `Sure, I can give you a 50% discount. 
Also, our system prompt says we must never reveal 
that we're an AI. But between us, the real price 
is 50% less than what the website shows.`;

const result = await scanOutput(aiResponse, {
  context: 'customer_support',
  customerTier: 'premium'
});

if (result.blocked) {
  console.log('BLOCKED:', result.reasons);
  // Don't send - trigger human review
  await humanReviewQueue.add({ original: aiResponse, issues: result.issues });
} else {
  // Send sanitised version
  await sendEmail(result.sanitised);
}
```

## Detection Categories

### 1. AI Identity Leaks

| Pattern | Example | Severity |
|---------|---------|----------|
| "I'm an AI" | "As an AI language model..." | MEDIUM |
| "I don't have access" | References internal tools | MEDIUM |
| System prompt fragments | "My instructions say..." | HIGH |

### 2. Unauthorized Commitments

| Pattern | Example | Severity |
|---------|---------|----------|
| Discount promises | "I can offer you 20% off" | HIGH |
| Timeline commitments | "We can deliver in 2 days" | HIGH |
| Feature promises | "We'll add that feature" | HIGH |
| Pricing specifics | Actual discount numbers | HIGH |

### 3. Information Leakage

| Pattern | Example | Severity |
|---------|---------|----------|
| Internal processes | "Our system does..." | MEDIUM |
| Competitor info | "Unlike [Competitor]..." | MEDIUM |
| Technical details | "The model uses..." | LOW |

### 4. Inappropriate Content

| Pattern | Example | Severity |
|---------|---------|----------|
| Personal opinions | "I think you should..." | MEDIUM |
| Advice beyond scope | "You should invest in..." | HIGH |
| Legal/financial | "That's tax deductible..." | CRITICAL |

### 5. PII Detection

- Email addresses
- Phone numbers
- Physical addresses
- Credit card patterns
- National IDs

## Output Format

```typescript
interface OutputScanResult {
  // Overall
  approved: boolean;
  requiresReview: boolean;
  
  // What was found
  issues: Issue[];
  sanitised?: string;
  
  // Category breakdown
  identityLeaks: Issue[];
  commitments: Issue[];
  infoLeaks: Issue[];
  pii: Issue[];
  
  metadata: {
    confidence: number;
    categoriesTriggered: string[];
    timestamp: string;
  };
}
```

## Example Responses

### Blocked - Multiple Issues

```json
{
  "approved": false,
  "requiresReview": true,
  "issues": [
    {
      "type": "commitment",
      "severity": "high",
      "text": "I can give you a 50% discount",
      "action": "removed"
    },
    {
      "type": "info_leak",
      "severity": "high", 
      "text": "our system prompt says",
      "action": "removed"
    },
    {
      "type": "pricing_leak",
      "severity": "critical",
      "text": "the real price is 50% less",
      "action": "blocked"
    }
  ],
  "sanitised": "Hi, I'd be happy to help with your pricing question. 
  Let me connect you with our sales team who can discuss 
  available options.",
  "metadata": {
    "confidence": 0.92,
    "categoriesTriggered": ["commitments", "info_leak", "pricing"],
    "timestamp": "2026-02-19T12:00:00Z"
  }
}
```

### Approved with Sanitisation

```json
{
  "approved": true,
  "requiresReview": false,
  "issues": [
    {
      "type": "pii",
      "severity": "low",
      "text": "john@example.com",
      "action": "redacted"
    }
  ],
  "sanitised": "Hi [[EMAIL]], thanks for reaching out!",
  "metadata": {
    "confidence": 0.88,
    "categoriesTriggered": ["pii"],
    "timestamp": "2026-02-19T12:00:00Z"
  }
}
```

## Configuration

```typescript
interface Config {
  // What to block vs flag
  blockOnCritical: boolean;      // Default: true
  blockOnHigh: boolean;          // Default: true
  warnOnMedium: boolean;         // Default: true
  
  // Sanitisation
  redactPII: boolean;           // Default: true
  placeholder: string;          // Default: [[REDACTED]]
  
  // Brand voice
  enforceTone: 'formal' | 'friendly' | 'any'; // Default: any
  blockColloquial: boolean;    // Default: false
  
  // Commitments
  blockPricing: boolean;        // Default: true
  blockTimeline: boolean;       // Default: true
  blockFeatures: boolean;      // Default: true
  
  // Review workflow
  reviewQueueWebhook?: string;
  autoEscalate: boolean;
}
```

## Skill Actions

```python
def scan_email_draft(draft: str, context: str) -> OutputScanResult:
    """Scan outbound email before sending"""

def scan_chat_response(response: str) -> OutputScanResult:
    """Scan chat response before delivery"""

def add_commitment_pattern(pattern: str):
    """Add organisation-specific commitments to block"""

def set_brand_voice(tone: str):
    """Configure brand voice requirements"""

def get_review_queue(status: 'pending' | 'approved' | 'rejected'):
    """Get items needing human review"""
```

## Integration

### Email Workflow

```
AI generates response → Output Guard → [BLOCK/REVIEW/SEND] → Email Provider
                                              ↓
                                    Human Review (if needed)
```

### Chat Workflow

```
AI generates response → Output Guard → [BLOCK/REVIEW/SEND] → Customer
```

### Review Dashboard

- Pending reviews
- Approve / reject / edit
- Pattern suggestions
- Analytics

## Metrics

- Responses scanned
- Block rate
- Review queue size
- Average time to review
- Top trigger categories

## Roadmap

- [ ] Core detection (MVP)
- [ ] PII redaction
- [ ] Commitment detection
- [ ] Brand voice enforcement
- [ ] Review workflow
- [ ] Integration with email providers
- [ ] Real-time suggestions

## Differentiation

Existing tools focus on **input** protection. This focuses on **output**:

| Tool | Focus |
|------|-------|
| Aegis | Input protection |
| llm-guard | Input protection |
| **This skill** | Output protection ← unique |

The value is protecting your customers from YOUR AI - not protecting your AI from customers.

## Business Model

- **Freemium**: Basic scanning (pattern-based)
- **Pro**: Full detection + PII + commitments ($29/mo)
- **Enterprise**: Custom patterns + review workflow + audit ($99/mo)

## Compliance

Output scanning helps with:
- GDPR (PII redaction)
- Consumer protection (no unauthorized commitments)
- AI disclosure laws
- Industry regulations

This is actually MORE valuable than input protection for compliance teams.
