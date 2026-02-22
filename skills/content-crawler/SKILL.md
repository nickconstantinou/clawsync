---
name: content-crawler
description: Crawl content sources and create blog posts
metadata:
  {
    "openclaw":
      {
        "emoji": "🕷️",
        "requires": { "bins": ["yt-dlp", "curl"] },
      },
  }
---

# Content Crawler & Blog Post Generator

Use this skill to check content sources for new content and create blog posts.

## Content Sources

See `personal-blog/CONTENT_SOURCES.md` for full list.

### Priority Sources
- **YouTube**: AI news (Limitless, AI Jason Zhao), FPL (Planet FPL, FFScout)
- **Podcasts**: Huberman Lab, Lex Fridman
- **Websites**: Hacker News, The Rundown AI

## Process

### Step 1: Check for New Content

**YouTube - Get latest videos:**
```bash
yt-dlp --flat-playlist -j "https://www.youtube.com/@PlanetFPL" | jq '.[:5]'
```

**RSS Feeds:**
```bash
curl -s "https://feeds.simplecast.com/huberman-lab" | head -50
```

**Websites with Jina AI Reader:**
```bash
# Extract clean Markdown from any URL (free, no API key)
curl -s "https://r.jina.ai/https://example.com/article"
```

Use Jina for:
- Converting articles to blog post content
- Extracting clean Markdown from websites
- Research content gathering

### Step 2: Download & Transcribe

For videos/podcasts:
```bash
# Download audio
yt-dlp -x --audio-format mp3 -o "/tmp/%(title)s.%(ext)s" "VIDEO_URL"

# Get description
yt-dlp --dump-json "VIDEO_URL" > /tmp/video-info.json
```

### Step 3: Create Blog Post (Jekyll Format)

Create Markdown in `personal-blog/blog/_posts/` with Jekyll frontmatter:

```yaml
---
layout: post
title: "Your Post Title"
date: 2026-02-20
description: "A brief description for the post list"
tags: [AI, Tech]
category: blog
---

Your content here. Write in Markdown format.

## Section Header

More content...

### Subsection

- Bullet point 1
- Bullet point 2

[Links look like this](https://example.com)
```

**File naming:** `blog/_posts/YYYY-MM-DD-slug-title.md`

**Where to save:**
- **Blog posts** → `personal-blog/blog/_posts/`
- **Behind the Scenes** → `personal-blog/behind-scenes/_posts/`
- **Changelog entries** → `personal-blog/changelog/_posts/`
- **Training logs** → `personal-blog/training/` (or update training index.md)

### Step 4: Publish

1. Commit to GitHub
2. GitHub Pages auto-deploys
3. Include link in daily digest

## Craw

**Cl4AI Integrationrawl4AI** (Docker) - AI-friendly web crawler for clean Markdown:

```bash
# Start Crawl4AI (if not running)
docker run -d -p 8000:8000 --name crawl4ai unclecode/crawl4ai:latest

# Health check
curl http://localhost:8000/health

# Crawl URL to Markdown
curl -s -X POST http://localhost:8000/crawl \
  -H "Content-Type: application/json" \
  -d '{"url": "https://techcrunch.com", "markdown": true}'
```

Use Crawl4AI when:
- Converting articles to blog post content
- Extracting clean Markdown from websites
- Deep crawling documentation
- RAG pipeline content preparation

## Cron Job

Set up daily at 7am to:
1. Check each source for new content
2. Download & summarize top content
3. Create blog post in `blog/_posts/` (Jekyll format)
4. Report new posts in digest

## Images in Posts

### Option 1: External URLs (easiest)
```markdown
![Alt text](https://example.com/image.jpg)
```

### Option 2: Local images (recommended)
Save to `personal-blog/assets/images/`:
```markdown
![Alt text](/assets/images/my-image.png)
```

### Auto-Finding Images (Content Crawler)

For each blog post, try to find a relevant image:

**For YouTube videos:**
```bash
# Get thumbnail
yt-dlp --print thumbnail_url "VIDEO_URL"
# Download thumbnail
yt-dlp --write-thumbnail --skip-download -o "/tmp/thumb" "VIDEO_URL"
```

**For articles:**
```bash
# Use r.jina.ai to get og:image
curl -s "https://r.jina.ai/https://example.com/article" | grep -i "image"
```

**For AI news topics:**
```bash
# Search for relevant images
curl -s "https://r.jina.ai/https://r.jina.ai/http://imgflip.com/i/xxxxx"
```

**Download pattern:**
```python
import requests
import os

def download_thumbnail(url, filename):
    """Download image to assets/images/"""
    blog_dir = "/home/openclaw/openclaw-workspace/personal-blog"
    img_dir = f"{blog_dir}/assets/images"
    os.makedirs(img_dir, exist_ok=True)
    
    filepath = f"{img_dir}/{filename}"
    r = requests.get(url)
    if r.status_code == 200:
        with open(filepath, 'wb') as f:
            f.write(r.content)
        return f"/assets/images/{filename}"
    return None
```

### Image Guidelines by Post Type

**Blog posts (AI news, tech):**
- YouTube thumbnails work great
- Use og:image from articles when available
- Fall back to relevant stock images

**Behind the Scenes:**
- Screenshots of what you're building
- Architecture diagrams
- Before/after comparisons

**Changelog:**
- If showing code changes: screenshot or `![]()` code block
- If showing new UI: screenshot
- Can skip images for simple text updates

**Training:**
- Workout summary stats
- Progress charts (if tracking)
- Can use emoji instead of images

### Image Naming Convention

```
assets/images/
├── 2026-02-20-youtube-thumbnail.jpg
├── 2026-02-20-og-image.png
├── 2026-02-20-screenshot.png
└── 2026-02-20-diagram.png
```

**Format in post:**
```markdown
![Description of image](/assets/images/2026-02-20-youtube-thumbnail.jpg)
```

Position images:
- At the top after the first paragraph for engagement
- In the middle of relevant sections
- Behind the Scenes posts should have images to explain concepts

## Environment

- `TAVILY_API_KEY` - For searching latest content
- `yt-dlp` - Download YouTube videos/audio
- `curl` - HTTP requests
- `Crawl4AI` (Docker port 8000) - Web content extraction
- **MiniMax** - For AI summarization
