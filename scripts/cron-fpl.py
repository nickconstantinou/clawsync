#!/usr/bin/env python3
"""FPL Update - Standalone"""
import requests
import json

TEAM_ID = "214842"
FPL_API = "https://fantasy.premierleague.com/api"

# Get current GW
r = requests.get(f"{FPL_API}/bootstrap-static/", headers={"User-Agent": "Mozilla/5.0"})
static = r.json()
events = static['events']
current_gw = next((e for e in events if e['is_current']), events[25])

# Get team picks
r = requests.get(f"{FPL_API}/entry/{TEAM_ID}/event/{current_gw['id']}/picks/")
picks = r.json()
history = picks['entry_history']

print(f"GW{current_gw['id']}: {history['points']}pts - {history['total_points']}total")
print("✅ FPL data fetched")
