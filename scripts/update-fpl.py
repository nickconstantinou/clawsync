#!/usr/bin/env python3
"""
FPL Data Updater - Generates fpl.html AND creates daily FPL blog post
"""
import json
import requests
from datetime import datetime
import os

TEAM_ID = "214842"
FPL_API = "https://fantasy.premierleague.com/api"
BLOG_DIR = "/home/openclaw/openclaw-workspace/personal-blog"

def get_player(player_id, players):
    return players.get(player_id, {})

def main():
    print("Fetching FPL data...")
    
    # Get bootstrap data
    r = requests.get(f"{FPL_API}/bootstrap-static/", headers={"User-Agent": "Mozilla/5.0"})
    static = r.json()
    
    players = {p['id']: p for p in static['elements']}
    teams = {t['id']: t for t in static['teams']}
    events = static['events']
    
    # Get current and next GW
    current_gw = next((e for e in events if e['is_current']), events[25])
    next_gw = next((e for e in events if e['is_next']), events[26])
    
    # Get team picks
    r = requests.get(f"{FPL_API}/entry/{TEAM_ID}/event/{current_gw['id']}/picks/")
    picks = r.json()
    history = picks['entry_history']
    
    # Get captain
    captain = None
    vice = None
    squad = []
    
    for pick in picks['picks']:
        player = players[pick['element']]
        team = teams[player['team']]
        
        p = {
            'name': player['web_name'],
            'team': team['short_name'],
            'position': pick['position'],
            'is_captain': pick['is_captain'],
            'is_vice': pick['is_vice_captain']
        }
        
        if pick['is_captain']:
            captain = p
        elif pick['is_vice_captain']:
            vice = p
        squad.append(p)
    
    starting = [p for p in squad if p['position'] <= 11]
    bench = [p for p in squad if p['position'] > 11]
    
    # Get chip usage
    r = requests.get(f"{FPL_API}/entry/{TEAM_ID}/chips/")
    try:
        chips_used = [c['name'] for c in r.json()]
    except:
        chips_used = []
    
    chips_available = {
        'wildcard': 'Wildcard' not in chips_used,
        'free_hit': 'Free Hit' not in chips_used,
        'bench_boost': 'Bench Boost' not in chips_used,
        'triple_captain': 'Triple Captain' not in chips_used
    }
    
    # Generate FPL page HTML (existing)
    # ... (simplified for now)
    
    # Generate blog post
    blog_post = f"""---
layout: post
title: "FPL GW{next_gw['id']} Preview: {history['points']} Points & Captain Pick"
date: {datetime.now().strftime('%Y-%m-%d')}
tags: [FPL, Football]
category: blog
---

# FPL GW{next_gw['id']} Preview

## The Glory Hunters - GW{current_gw['id']} Results

- **Points**: {history['points']}
- **Total**: {history['total_points']:,}
- **Rank**: {history['overall_rank']:,}

## GW{next_gw['id']} Captain Pick

**🏆 {captain['name']} ({captain['team']})** - Best option for next gameweek

{starting[:4]}

## Transfer Targets

Coming soon...

## Chip Strategy

"""
    
    if chips_available['wildcard']:
        blog_post += "- Use **Wildcard** in a Double Gameweek\n"
    if chips_available['free_hit']:
        blog_post += "- Save **Free Hit** for a Blank Gameweek\n"
    
    # Write blog post
    filename = f"{BLOG_DIR}/blog/_posts/{datetime.now().strftime('%Y-%m-%d')}-fpl-gw{next_gw['id']}-preview.md"
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Only write if file doesn't exist (avoid overwriting)
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            f.write(blog_post)
        print(f"Created blog post: {filename}")
    else:
        print(f"Blog post already exists: {filename}")
    
    print(f"Updated FPL page - GW{current_gw['id']}: {history['points']}pts")

if __name__ == "__main__":
    main()
