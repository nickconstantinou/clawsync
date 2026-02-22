#!/usr/bin/env python3
"""YouTube Content Crawler"""
import subprocess
import os

BLOG_DIR = "/home/openclaw/openclaw-workspace/personal-blog"
os.chdir(BLOG_DIR)

CHANNELS = {
    "limitless": "UCCRxYlYOmLE2l5wxs3ckJtg",
}

# Check each channel
for name, channel_id in CHANNELS.items():
    result = subprocess.run(
        ["curl", "-s", f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"],
        capture_output=True, text=True
    )
    if "Error" not in result.stdout[:100]:
        print(f"✅ {name} RSS working")
    else:
        print(f"❌ {name} RSS failed")

print("✅ YouTube check done")
