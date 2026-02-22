---
name: tutor-data-collection
description: Research and collect UK tutor data for directory
metadata:
  {
    "openclaw":
      {
        "emoji": "🔍",
        "requires": { "bins": ["curl"] },
      },
  }
---

# Tutor Data Collection Skill

Research and collect UK tutor data for the directory.

## Data Sources

### Primary Sources
- **First Tutors** - Major UK directory
- **Superprof** - Large tutor marketplace
- **Tutor Hunt** - UK-wide coverage
- **The Tutor Association** - Verified tutors
- **Ofsted** - Registered childcare providers

### Free Data
- **Companies House** - Business registrations for tutoring companies
- **LinkedIn** - Individual tutors
- **Facebook Groups** - Local tutoring groups

### Research Commands

```bash
# Extract from tutor directory with Jina
curl -s "https://r.jina.ai/https://www.firsttutors.com/uk/tutors"

# Search for tutor directories
curl -s "https://r.jina.ai/https://www.tutorhunt.com/"

# Find local tutor associations
curl -s "https://r.jina.ai/https://www.tutors-association.org.uk/"
```

## Data to Collect

For each tutor:
- Name
- Location (city/area)
- Subjects taught
- Exam boards (AQA, OCR, Edexcel, WJEC)
- Levels (GCSE, A-Level, Primary, KS3)
- Hourly rate
- Ratings/reviews
- Contact details
- Availability
- Special needs experience

## Process

1. **Identify sources** — List 10+ UK tutor sites
2. **Extract data** — Use Jina or manual copy-paste
3. **Clean data** — Remove duplicates, format consistently
4. **Enrich** — Add missing fields with AI
5. **Store** — Save to CSV/JSON for directory

## Output Format

```json
{
  "name": "John Smith",
  "location": "London, SW1A",
  "subjects": ["Maths", "Physics"],
  "levels": ["GCSE", "A-Level"],
  "exam_boards": ["AQA", "Edexcel"],
  "hourly_rate": 35,
  "rating": 4.8,
  "verified": true
}
```

## Target

- 500+ tutors by launch
- 50+ subjects covered
- All major UK cities
