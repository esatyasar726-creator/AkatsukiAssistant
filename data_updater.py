import requests
import pandas as pd
import json
import os
import logging
from io import StringIO

# Config
CHAR_DB_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQHxqiuCWeLcndKBkz-nl9xwN3q7Qhbad3QRGFZflTpG8NIs2s2u0lUpqAqPA3mh92uDiRSgzdIdHox/pub?output=csv"
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

def contains_chinese(s):
    return any('\u4e00' <= char <= '\u9fff' for char in s)

def parse_characters(df):
    characters = {}
    if df is None: return characters

    start_rows = df[df['Unnamed: 1'].notna()].index.tolist()
    logging.info(f"Found {len(start_rows)} character starts in the spreadsheet.")

    for i in range(len(start_rows)):
        start = start_rows[i]
        end = start_rows[i+1] if i + 1 < len(start_rows) else len(df)
        block = df.iloc[start:end]

        # Name extraction & cleaning
        raw_name = str(block.iloc[0]['Unnamed: 1'])
        lines = [line.strip() for line in raw_name.split('\n') if line.strip()]
        english_lines = [line for line in lines if not contains_chinese(line)]
        name = " ".join(english_lines).strip()
        if not name:
            continue

        key = name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")

        rg_type = str(block.iloc[0]['RG TYPE']).strip()
        if rg_type == "nan":
            rg_type = "Unknown"

        talent_color = str(block.iloc[0]['CHARACTER CLASS\nTALENT COLOR']).strip()
        if talent_color == "nan":
            talent_color = "Unknown"

        # Talent extraction
        skill_header_idx = None
        for r_idx in range(1, len(block)):
            if str(block.iloc[r_idx]['SKILL DESCRIPTION']).strip() == 'Skill':
                skill_header_idx = r_idx
                break
        if skill_header_idx is None:
            skill_header_idx = 2

        talent_text = []
        for r_idx in range(1, skill_header_idx):
            row = block.iloc[r_idx]
            r_5 = str(row.get('Unnamed: 5', '')).strip()
            r_6 = str(row.get('Unnamed: 6', '')).strip()
            r_7 = str(row.get('Unnamed: 7', '')).strip()
            if r_5 and r_5 != 'nan':
                talent_text.append(f"Rank 4-8-12: {r_5}")
            if r_6 and r_6 != 'nan':
                talent_text.append(f"Rank 9: {r_6}")
            if r_7 and r_7 != 'nan':
                talent_text.append(f"Rank 13: {r_7}")

        # Skills extraction
        skills = {}
        for r_idx in range(skill_header_idx + 1, len(block)):
            row = block.iloc[r_idx]
            desc = str(row.get('SKILL DESCRIPTION', '')).strip()
            r_5 = str(row.get('Unnamed: 5', '')).strip()
            r_6 = str(row.get('Unnamed: 6', '')).strip()
            r_7 = str(row.get('Unnamed: 7', '')).strip()

            if desc in ['Before Liberation', 'After Liberation']:
                skills[desc] = {
                    's1': r_5 if r_5 and r_5 != 'nan' else '',
                    's2': r_6 if r_6 and r_6 != 'nan' else '',
                    's3_weapon': r_7 if r_7 and r_7 != 'nan' else ''
                }
            elif desc in ['Assist', 'Guard']:
                skills[desc] = r_5 if r_5 and r_5 != 'nan' else ''

        characters[key] = {
            "id": key,
            "name": name,
            "type": rg_type,
            "talent_color": talent_color,
            "description": f"A powerful character of type {rg_type} with {talent_color} talent rating.",
            "talents": talent_text,
            "skills": skills,
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

    # Fetch from Spreadsheet
    df = fetch_sheet_data(CHAR_DB_URL)
    chars = parse_characters(df)

    # Save to JSON
    save_json("characters.json", chars)
    logging.info(f"Update complete. {len(chars)} characters imported and saved.")

if __name__ == "__main__":
    update_database()
