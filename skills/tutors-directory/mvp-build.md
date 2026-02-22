---
name: tutor-directory-mvp
description: Build MVP for UK tutors directory
metadata:
  {
    "openclaw":
      {
        "emoji": "🛠️",
        "requires": { "bins": [] },
      },
  }
---

# Tutor Directory MVP Skill

Build a simple, functional directory for UK tutors.

## Tech Stack

- **Hosting**: GitHub Pages (free)
- **Styling**: Custom CSS (match ExamPulse brand)
- **Data**: JSON file (simple, no DB needed for MVP)
- **Search**: Client-side JavaScript

## Page Structure

### 1. Homepage (index.html)
- Hero: "Find the Perfect Tutor for Your Child"
- Search bar: Subject + Location
- Featured tutors
- How it works (3 steps)
- CTA: "List Your Tutoring Business"

### 2. Search Results
- Filter by: Subject, Location, Price, Rating
- Sort by: Relevance, Price, Rating
- Tutor cards with key info
- Pagination

### 3. Tutor Profile
- Name, photo placeholder
- Subjects & levels
- Hourly rate
- Location
- Reviews summary
- "Contact Tutor" button

### 4. Tutor Sign-up (for listing)
- Simple form: Name, email, subjects, rates
- Confirmation message

## Key Features

### Search Functionality
```javascript
function searchTutors(query) {
  return tutors.filter(t => 
    t.subjects.some(s => s.toLowerCase().includes(query)) ||
    t.location.toLowerCase().includes(query)
  );
}
```

### Filter Options
- Subject (Maths, English, Science, etc.)
- Level (GCSE, A-Level, Primary)
- Price range (£20-£50, £50-£80, £80+)
- Location (UK cities)
- Rating (4+, 4.5+, 5.0)

### Tutor Card Design
- Name
- Subjects (badges)
- Location
- Hourly rate
- Star rating
- "View Profile" button

## CSS Variables (Match ExamPulse)

```css
:root {
  --primary: #0F172A;
  --accent: #F97316;
  --bg: #FFFFFF;
  --text: #1E293B;
  --text-muted: #64748B;
  --border: #E2E8F0;
}
```

## Files to Create

1. `index.html` - Homepage with search
2. `search.html` - Results page
3. `tutor.html` - Profile template
4. `list.html` - Tutor sign-up
5. `data/tutors.json` - Tutor database
6. `styles.css` - Shared styles

## Launch Checklist

- [ ] Homepage loads
- [ ] Search works
- [ ] Filters work
- [ ] Tutor profiles display
- [ ] Mobile responsive
- [ ] 50 tutors listed
- [ ] Contact form works
