#!/bin/bash
# Daily Content Crawler for Nick's Blog
# Run at 7am daily

BLOG_DIR="/home/openclaw/openclaw-workspace/personal-blog"
MARKETING_DIR="/home/openclaw/openclaw-workspace/exam-pulse-marketing"

echo "=== Content Crawler - $(date) ==="

# Sources to check
echo "Checking sources for new content..."

# 1. Limitless AI (YouTube)
echo "Checking Limitless AI..."
LIMITLESS_NEWS=$(curl -s -X POST https://api.tavily.com/search \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "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",
    "query": "AI news today",
    "max_results": 3
  }' | jq -r '.results[0].title')

echo "Latest AI news: $LIMITLESS_NEWS"

# 2. Planet FPL
echo "Checking Planet FPL..."
FPL_NEWS=$(curl -s -X POST https://api.tavily.com/search \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "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",
    "query": "FPL tips GW27 2026",
    "max_results": 2
  }' | jq -r '.results[0].title')

echo "Latest FPL: $FPL_NEWS"

# 3. Huberman Lab
echo "Checking Huberman Lab..."
HUBERMAN_NEWS=$(curl -s -X POST https://api.tavily.com/search \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "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",
    "query": "Huberman Lab podcast latest 2026",
    "max_results": 2
  }' | jq -r '.results[0].title')

echo "Latest Huberman: $HUBERMAN_NEWS"

# Create summary for digest
echo ""
echo "=== Summary for Digest ==="
echo "AI: $LIMITLESS_NEWS"
echo "FPL: $FPL_NEWS"  
echo "Health: $HUBERMAN_NEWS"

# Check if there are new posts to publish
NEW_POSTS=""
if [ -n "$LIMITLESS_NEWS" ]; then
  NEW_POSTS="$NEW_POSTS\n- AI News: $LIMITLESS_NEWS"
fi

echo ""
echo "New posts to create: $NEW_POSTS"

# Note: Actual blog post creation would require more complex parsing
# For now, just report what's found

echo "=== Done ==="
