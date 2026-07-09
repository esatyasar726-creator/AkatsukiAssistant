from rapidfuzz import process
from game_data import CHARACTERS, CARDS, GENERAL_KNOWLEDGE
from banner_data import REFERENCE_DATE, REFERENCE_DAY
from datetime import datetime, timedelta

def find_best_match(query, choices):
    if not query:
        return None
    result = process.extractOne(query, choices)
    if result:
        best_match, score, index = result
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

    return "I'm not sure about that. I specialize in Bleach Mobile 3D cards and game mechanics. Try asking or use /cardinfo!"
