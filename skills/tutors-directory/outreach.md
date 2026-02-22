---
name: tutor-outreach
description: Outreach to get tutors listed on the directory
metadata:
  {
    "openclaw":
      {
        "emoji": "📧",
        "requires": { "bins": [] },
      },
  }
---

# Tutor Outreach Skill

Get tutors to list on the directory using cold outreach.

## Strategy

### Free First, Then Paid
- **Phase 1**: 50 free listings to build database
- **Phase 2**: Convert to paid leads
- **Phase 3**: Premium listings

### Outreach Channels

1. **Email** — Direct to tutors found in research
2. **Social** — Twitter, LinkedIn, Facebook Groups
3. **Local** — Contact schools, parent groups
4. **Partnerships** — Exam centres, tuition centres

## Email Templates

### Template 1: Initial Outreach (Free)
```
Subject: Free listing for UK tutors

Hi [Name],

I'm building the UK's most comprehensive tutor directory - [Directory Name].

I'm offering **50 free listings** to tutors to launch the directory.

To claim your free listing:
1. Fill in this form: [link]
2. We'll verify and publish within 24 hours

No catch - completely free.

[Link to form]

Best,
[Your name]
```

### Template 2: Follow-up
```
Subject: Reminder - Free tutor listing

Hi [Name],

Just following up on my last email.

We still have 20 free spots left for UK tutors.

List here: [link]

Best,
[Your name]
```

### Template 3: Paid Promotion
```
Subject: Get more students with [Directory Name]

Hi [Name],

Parents are searching for tutors like you on [Directory Name].

Our lead generation starts at £30 per verified lead.

Get 3 leads for £80:
[link]

Best,
[Your name]
```

## Scripts

### Cold Email (copy/paste)
```bash
# Find tutor emails from research
grep -r "email" tutor_data.json | cut -d'"' -f4 | head -50
```

### Twitter Outreach
```bash
# Search for UK tutors on Twitter
# RT this if you're a UK tutor looking for more students
# DM them with: "Hey! List on [directory] - free for first 50 tutors"
```

## Numbers Target

| Week | Emails Sent | Replies | Listings |
|------|-------------|---------|----------|
| 1 | 100 | 10 | 10 |
| 2 | 100 | 15 | 15 |
| 3 | 100 | 20 | 15 |
| 4 | 50 | 10 | 10 |
| **Total** | **350** | **55** | **50** |

## Key Messages

### For Tutors
- "More students, less marketing hassle"
- "We handle the leads, you handle the teaching"
- "Free to list, only pay for leads"

### For Parents
- "Verified tutors, real reviews"
- "Compare prices, book instantly"
- "Find tutors near you"

## Tracking

Track in a simple spreadsheet:
- Tutor name
- Email
- Date contacted
- Response (yes/no)
- Listed (yes/no)
- Paid (yes/no)
