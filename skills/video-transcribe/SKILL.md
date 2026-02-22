---
name: video-transcribe
description: Find YouTube videos, download, transcribe and summarize using Tavily + Gemini
metadata:
  {
    "openclaw":
      {
        "emoji": "🎬",
        "requires": { "bins": ["yt-dlp", "ffmpeg"] },
      },
  }
---

# Video Transcribe & Summarize

Use this skill to find YouTube videos, download them, and generate summaries using Tavily + Gemini.

## When to use

- User asks to "summarize this video" or "transcribe this YouTube"
- Find videos on a topic and summarize them
- Extract key insights from video content
- Create show notes from video

## Process

### Step 1: Find Related Videos (Tavily Search)

First, search for relevant videos on the topic using Tavily:

```bash
curl -s -X POST https://api.tavily.com/search \
  -H "Authorization: Bearer $TAVILY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "your topic youtube educational video", "max_results": 5}'
```

Or use the tavily skill to search for relevant videos.

### Step 2: Download Video/Audio

Download best audio from YouTube:

```bash
yt-dlp -f "bestaudio[ext=m4a]" -o "/tmp/%(title)s.%(ext)s" "VIDEO_URL"
```

Or with video:

```bash
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]" -o "/tmp/%(title)s.%(ext)s" "VIDEO_URL"
```

### Step 3: Extract Audio (if video downloaded)

```bash
# Extract full audio
ffmpeg -i "input.mp4" -vn -acodec libmp3lame -q:a 2 "/tmp/audio.mp3"
```

### Step 3b: Split Audio into Chunks (optional, for long videos)

For videos > 10 minutes, split into chunks for easier processing:

```bash
# Split into 10-minute chunks
ffmpeg -i "/tmp/audio.mp3" -f segment -segment_time 600 -c copy "/tmp/chunk_%03d.mp3"

# Or split by duration
ffmpeg -i "input.mp4" -t 600 -c copy "/tmp/part1.mp4"  # first 10 mins
```

### Step 4: Summarize with MiniMax

Use MiniMax (or OpenClaw's model) to summarize. Pass the video URL and ask for:

```
Summarize this YouTube video: VIDEO_URL

Provide:
- Key takeaways (bullet points)
- Timestamps for main sections
- Actionable insights
```

Or use web_fetch to get video details, then summarize using OpenClaw's chat.

### Step 5: Clean Up

Delete downloaded files to free up space:

```bash
rm -f /tmp/*.mp3 /tmp/*.mp4 /tmp/*.m4a /tmp/*.webm
```

Or delete specific file:

```bash
rm -f "/tmp/your-video-title.mp3"

## Environment

- `TAVILY_API_KEY` - For finding related videos (tavily skill)
- `yt-dlp` - Download YouTube videos
- `ffmpeg` - Extract audio from video
- **MiniMax** - For AI summarization (using OpenClaw's model)

## Tips

- For long videos, consider downloading only the first 10 minutes: `--range 0:10:00`
- **For long videos, split audio into 5-10 min chunks** using ffmpeg segmenter
- Use `-x` flag with yt-dlp to extract audio directly: `yt-dlp -x --audio-format mp3 URL`
- Use MiniMax via OpenClaw for summarization
- Start with Tavily search to find the best videos on a topic before downloading
