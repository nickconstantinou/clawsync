# UK Tutors Marketing Skill

## Overview
Tools and workflows for marketing the UK Tutors Directory.

## Quick Reference

### Site
- **URL:** https://nickconstantinou.github.io/uk-tutors-directory/
- **Repo:** nickconstantinou/uk-tutors-directory
- **Blog:** /blog/ directory

### Analytics
- **PostHog:** Using credentials file (see credentials/posthog.json)
- **Events Tracked:**
  - `contact_modal_opened`
  - `search_performed`
  - `lead_submitted`

### Supabase
- **Project:** araqigsimkjsmwhnjesv
- **Tables:**
  - `tutors` - tutor profiles
  - `leads` - parent enquiries

### Key Files
- Marketing docs: `/home/openclaw/openclaw-workspace/uk-tutors-marketing/`
  - personas.md
  - lead-magnets.md
  - site-analysis.md
  - campaign-strategy.md

## Workflows

### Add New Blog Post
1. Create HTML in `/tmp/uk-tutors-directory/blog/`
2. Add nav link in index.html if new section
3. Commit and push

### Add New City
1. Scrape tutors using Outscraper (see /skills/outscraper/)
2. Enrich with Jina AI Reader
3. Insert to Supabase
4. Deploy

### Create Lead Magnet
1. Write content (PDF or HTML)
2. Add capture form
3. Add to site under /blog/

### Run Campaign
1. Check PostHog for current metrics
2. Review campaign-strategy.md
3. Execute phase tasks
4. Track results

## Cron Jobs
- No scheduled campaigns yet
- Consider weekly content crawler for blog

## Lead Flow
1. Parent searches tutors
2. Clicks "Contact Tutor"
3. Fills form → stored in `leads` table
4. (Future) Email sent to parent + tutor
