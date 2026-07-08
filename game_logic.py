from fuzzywuzzy import process
from game_data import CHARACTERS, CARDS, GENERAL_KNOWLEDGE
from banner_data import REFERENCE_DATE, REFERENCE_DAY
from datetime import datetime, timedelta

def find_best_match(query, choices):
    if not query:
        return None
    best_match, score = process.extractOne(query, choices)
    if score > 70: # Threshold for fuzzy matching
        return best_match
    return None

def get_current_day():
    ref_date = datetime.strptime(REFERENCE_DATE, "%Y-%m-%d")
    today = datetime.utcnow()
    delta_days = (today - ref_date).days
    return REFERENCE_DAY + delta_days

def get_availability_text(item_name):
    # This is a simplified logic. In a real scenario, you'd have a schedule for each card.
    # For now, we use the status from CARDS or default to 'Check event rotation'.
    day = get_current_day()

    # Example logic: items cycle every 30 days
    # If day % 30 is between 0 and 5, it's available.
    is_available = (day % 30) < 5

    if is_available:
        return "Available now ✅"
    else:
        wait_days = 30 - (day % 30)
        return f"Available in {wait_days} days ⏳ (Estimated)"

def get_build_response(char_query):
    best_match = find_best_match(char_query.lower(), list(CHARACTERS.keys()))
    if not best_match:
        return "❌ Character not found in our database. Try another one!"

    char = CHARACTERS[best_match]
    build = char['build']

    response = (
        f"⚔️ **BEST BUILD FOR {char['name'].upper()}** ⚔️\n\n"
        f"👤 **Main Character:**\n{build['main']}\n\n"
        f"👥 **Assist Characters:**\n- " + "\n- ".join(build['assists']) + "\n\n"
        f"🛡 **Guard Characters:**\n- " + "\n- ".join(build['guards']) + "\n\n"
        f"🃏 **Recommended Cards:**\n"
    )

    for card in build['cards']:
        response += f"- {card} ({get_availability_text(card)})\n"

    response += (
        f"\n🔗 **Bond Recommendations:**\n"
        f"⚔️ **Attack Bonds:**\n- " + "\n- ".join(build['bonds']['attack']) + "\n\n"
        f"❤️ **HP Bonds:**\n- " + "\n- ".join(build['bonds']['hp']) + "\n\n"
        f"🛡 **Defense/Armor Bonds:**\n- " + "\n- ".join(build['bonds']['defense'])
    )
    return response

def get_card_analysis(card_query):
    best_match = find_best_match(card_query.lower(), list(CARDS.keys()))
    if not best_match:
        return "❌ Card not found in our database."

    card = CARDS[best_match]
    s = card['skills']

    response = (
        f"🃏 **Card:** {card['name']}\n"
        f"📌 **Type:** {card['type']}\n\n"
        f"⚔️ **Skill Analysis:**\n\n"
        f"**Skill 1:**\n- Effect: {s['skill1']['effect']}\n- Usage: {s['skill1']['usage']}\n- Best situation: {s['skill1']['situation']}\n\n"
        f"**Skill 2:**\n- Effect: {s['skill2']['effect']}\n- Usage: {s['skill2']['usage']}\n- Best situation: {s['skill2']['situation']}\n\n"
        f"**Skill 3:**\n- Effect: {s['skill3']['effect']}\n- Usage: {s['skill3']['usage']}\n- Special advantages: {s['skill3']['advantages']}\n\n"
        f"🌟 **Card Advantages:**\n{card['advantages']}\n\n"
        f"⚠️ **Card Disadvantages:**\n{card['disadvantages']}\n\n"
        f"🔥 **Meta Usage:**\n{card['meta_usage']}\n\n"
        f"🆚 **Counter Information:**\n\n"
        f"**Strong Against:**\n- " + "\n- ".join(card['counters']['strong_against']) + "\n\n"
        f"**Countered By:**\n- " + "\n- ".join(card['counters']['countered_by']) + "\n\n"
        f"🔗 **Best Bonds:**\n"
        f"⚔️ Attack Bonds: {', '.join(card['bonds']['attack'])}\n"
        f"❤️ HP Bonds: {', '.join(card['bonds']['hp'])}\n"
        f"🛡 Defense Bonds: {', '.join(card['bonds']['defense'])}\n\n"
        f"🎯 **Best Builds:**\n"
        f"- Main: {', '.join(card['best_builds']['main'])}\n"
        f"- Assists: {', '.join(card['best_builds']['assists'])}\n"
        f"- Guards: {', '.join(card['best_builds']['guards'])}\n\n"
        f"📊 **Final Rating:**\n"
        f"- Overall: {card['rating']['overall']}\n"
        f"- PvP: {card['rating']['pvp']}\n"
        f"- PvE: {card['rating']['pve']}\n"
        f"- Investment Priority: {card['rating']['priority']}"
    )
    return response

def get_ai_response(query):
    # Simple keyword matching for general questions
    query_lower = query.lower()
    for key, value in GENERAL_KNOWLEDGE.items():
        if key in query_lower:
            return value

    # Check if they are asking about a character build
    if "build" in query_lower:
        # Try to extract character name - very simple approach
        words = query_lower.split()
        for word in words:
            if word in CHARACTERS:
                return get_build_response(word)
        # Fallback to whole query minus 'build'
        potential_name = query_lower.replace("build", "").replace("for", "").strip()
        if potential_name:
            match = find_best_match(potential_name, list(CHARACTERS.keys()))
            if match:
                return get_build_response(match)

    return "I'm not sure about that. I specialize in Bleach Mobile 3D builds, cards, and game mechanics. Try asking 'build for SP Aizen' or use /cardinfo!"
