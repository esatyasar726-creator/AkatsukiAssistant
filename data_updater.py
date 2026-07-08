import requests
import pandas as pd
import json
import os
import logging
from bs4 import BeautifulSoup
from io import StringIO

# Config
# Note: Bit.ly links usually redirect to Google Sheets or Wikis.
# The user provided bit.ly/bm3dchar and a direct spreadsheet link.
CHAR_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQHxqiuCWeLcndKBkz-nl9xwN3q7Qhbad3QRGFZflTpG8NIs2s2u0lUpqAqPA3mh92uDiRSgzdIdHox/pub?output=csv"
WIKI_BASE_URL = "https://bleachm3d.fandom.com/wiki/BleachM3d_Wiki"
DATA_DIR = "data"

logging.basicConfig(level=logging.INFO)

def ensure_dirs():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def fetch_sheet_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            csv_data = StringIO(response.text)
            df = pd.read_csv(csv_data)
            return df
    except Exception as e:
        logging.error(f"Error fetching sheet data: {e}")
    return None

def parse_characters(df):
    characters = {}
    if df is None: return characters

    # Simple parsing logic - in reality, Bleach spreadsheet layouts can be messy
    for index, row in df.iterrows():
        raw_name = str(row.get('NAME', ''))
        if not raw_name or raw_name == 'nan': continue

        # Extract clean name (first line of cell usually)
        name = raw_name.split('\n')[0].strip()
        key = name.lower().replace(" ", "_")

        characters[key] = {
            "name": name,
            "type": str(row.get('RG TYPE', 'Unknown')),
            "description": str(row.get('CHARACTER CLASS\nTALENT COLOR', '')).replace('\n', ' '),
            "skills": [str(row.get('SKILL DESCRIPTION', ''))], # Simplified
            "bonds": {
                "attack": [],
                "hp": [],
                "defense": []
            },
            "source": "Spreadsheet"
        }
    return characters

def save_json(filename, data):
    with open(os.path.join(DATA_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def update_database():
    ensure_dirs()
    logging.info("Starting database update from external sources...")

    # 1. Fetch from Spreadsheet
    df = fetch_sheet_data(CHAR_DB_URL)
    chars = parse_characters(df)

    # 2. Mock Wiki Fetch (since actual scraping requires per-page iteration)
    # This would normally crawl WIKI_BASE_URL

    # Merge Logic (Prioritizing Character DB)
    save_json("characters.json", chars)

    # Mocking Cards and Meta for now as Spreadsheet mainly has Chars/Bonds
    cards = {
        "final_fusion": {
            "name": "Final Fusion",
            "type": "Attack",
            "rarity": "SP",
            "skills": {
                "skill1": {"name": "Fragor", "effect": "DMG Up", "cooldown": "15s", "best_usage": "Opener"},
                "skill2": {"name": "Ultra-Fragor", "effect": "Def Down", "cooldown": "20s", "best_usage": "Mid-combo"},
                "skill3": {"name": "Transcendence", "explanation": "Huge AOE", "hidden_interactions": "None", "priority": "High", "combos": "1-2-3"}
            },
            "stats": {"hp": "10000", "attack": "2500", "defense": "800", "pierce": "500", "crit": "400", "block": "300"},
            "analysis": {"pvp": "S Tier", "pve": "A Tier", "guild_war": "S Tier", "arena": "S Tier"},
            "strategy": {"weaknesses": "None", "strengths": "Burst", "strong_against": ["Tanks"], "countered_by": ["Silence"], "best_synergies": ["Mugetsu"]},
            "recommendations": {"bonds": ["Aizen"], "team": ["SP Team"], "assist": "Nelliel", "guard": "Yamamoto"},
            "rating": {"overall": "9.5/10", "investment": "High"},
            "expert_opinion": "A must have for any serious ATK build."
        }
    }
    save_json("cards.json", cards)

    logging.info(f"Update complete. {len(chars)} characters imported.")

if __name__ == "__main__":
    update_database()
