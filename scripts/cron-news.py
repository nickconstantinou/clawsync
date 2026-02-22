#!/usr/bin/env python3
"""News Content Crawler"""
import subprocess
import json

# AI Secret
result = subprocess.run(["curl", "-s", "https://aisecret.us/rss/"], capture_output=True, text=True)
if "AI Secret" in result.stdout:
    print("✅ AI Secret working")

# Hacker News
result = subprocess.run([
    "curl", "-s", 
    "https://hn.algolia.com/api/v1/search_by_date?tags=story&hitsPerPage=3"
], capture_output=True, text=True)
try:
    data = json.loads(result.stdout)
    print(f"✅ Hacker News working ({len(data.get('hits',[]))} stories)")
except:
    print("❌ Hacker News failed")

print("✅ News check done")
