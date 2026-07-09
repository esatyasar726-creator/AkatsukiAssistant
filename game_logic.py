import re
import math
import random
from fuzzywuzzy import process
from banner_data import REFERENCE_DATE, REFERENCE_DAY
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
from data_manager import data_manager

# Legacy fallback general knowledge matching
GENERAL_KNOWLEDGE = {
    "how to get sp characters": "SP characters can be obtained through Special Gacha events, typically rotating every 2 weeks. Save your crystals! 💎",
    "best build for beginners": "Focus on Ichigo (Vasto Lorde) or Ulquiorra (Resurrección). They are easier to build and very effective in the early-mid game! ⚔️",
    "what are guards": "Guards provide defensive stats and special protective skills when your health drops below a certain threshold. 🛡️"
}

# Memory storage
# Key: (chat_id, user_id) -> dict with 'name', 'favorite_char', 'history' (list of tuples of (user_msg, bot_msg))
conversation_memory = {}

def get_memory(chat_id, user_id):
    key = (chat_id, user_id)
    if key not in conversation_memory:
        conversation_memory[key] = {
            "name": None,
            "favorite_char": None,
            "history": []
        }
    return conversation_memory[key]

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
    day = get_current_day()
    is_available = (day % 30) < 5
    if is_available:
        return "Available now ✅"
    else:
        wait_days = 30 - (day % 30)
        return f"Available in {wait_days} days ⏳ (Estimated)"

# Comprehensive build and card lookup that automatic handles ANY character
def get_build_response(char_query):
    char = data_manager.find_item("characters", char_query)
    if not char:
        return f"❌ Character '{char_query}' not found in our database. Try another one!"

    build = char.get('build', {})

    # Separation into ATTACK, HP, and DEFENSE categories with ALL recommended bonds (Requirement 3 & 4)
    response = (
        f"⚔️ **PROFESSIONAL BUILD & ANALYSIS FOR {char['name'].upper()}** ⚔️\n\n"
        f"👤 **Main Character:** {build.get('main', char['name'])}\n"
        f"📌 **Rarity / Type:** {char.get('type', 'Unknown')}\n"
        f"⭐ **Talent Rating:** {char.get('talent_color', 'N/A')}\n\n"
        f"👥 **Recommended Assist Characters:**\n" + "\n".join([f"- {a}" for a in build.get('assists', [])]) + "\n\n"
        f"🛡️ **Recommended Guard Characters:**\n" + "\n".join([f"- {g}" for g in build.get('guards', [])]) + "\n\n"
        f"🃏 **Recommended Cards:**\n"
    )

    for card in build.get('cards', []):
        response += f"- {card} ({get_availability_text(card)})\n"

    b = build.get('bonds', {})
    b_atk = b.get('attack', [])
    b_hp = b.get('hp', [])
    b_def = b.get('defense', [])

    response += (
        f"\n🔗 **ALL RECOMMENDED BONDS (DO NOT SHORTEN)**\n\n"
        f"⚔️ **ALL Recommended Attack Bonds**\n" + "\n".join([f"- {x}" for x in b_atk]) + "\n\n"
        f"❤️ **ALL Recommended HP Bonds**\n" + "\n".join([f"- {x}" for x in b_hp]) + "\n\n"
        f"🛡️ **ALL Recommended Defense/Armor Bonds**\n" + "\n".join([f"- {x}" for x in b_def]) + "\n\n"
        f"⚡ **Talents:**\n" + "\n".join([f"- {t}" for t in char.get('talents', [])]) + "\n\n"
        f"⚙️ **Recommended Gear:**\n" + "\n".join([f"- {g}" for g in build.get('gear', [])]) + "\n\n"
        f"💎 **Recommended Accessories:**\n" + "\n".join([f"- {a}" for a in build.get('accessories', [])]) + "\n\n"
        f"🎮 **Gameplay Tips:**\n{build.get('tips', 'N/A')}\n\n"
        f"💪 **Strengths:**\n{build.get('strengths', 'N/A')}\n\n"
        f"⚠️ **Weaknesses:**\n{build.get('weaknesses', 'N/A')}\n\n"
        f"🆚 **Counters:**\n" + "\n".join([f"- {c}" for c in build.get('counters', [])]) + "\n\n"
        f"🤝 **Synergies:**\n" + "\n".join([f"- {s}" for s in build.get('synergies', [])]) + "\n\n"
        f"💰 **Investment Priority:** {build.get('investment', 'N/A')}\n"
        f"🏆 **PvP Rating:** {build.get('pvp_rating', 'N/A')}\n"
        f"👹 **PvE Rating:** {build.get('pve_rating', 'N/A')}"
    )
    return response

def get_card_analysis(card_query):
    card = data_manager.find_item("cards", card_query)
    if not card:
        return f"❌ Card '{card_query}' not found in our database."

    s = card.get('skills', {})

    response = (
        f"🃏 **CARD PROFILE: {card['name'].upper()}**\n"
        f"📌 **Type:** {card.get('type', 'N/A')} | **Rarity:** {card.get('rarity', 'N/A')}\n\n"
        f"📖 **Description:** {card.get('description', 'N/A')}\n\n"
        f"⚔️ **Skill Analysis:**\n\n"
    )

    for i in range(1, 4):
        sk = s.get(f'skill{i}', {})
        if sk:
            response += f"**Skill {i} ({sk.get('name', 'N/A')})**\n"
            if i < 3:
                response += f"- Effect: {sk.get('effect', 'N/A')}\n- Cooldown: {sk.get('cooldown', 'N/A')}\n- Best Usage: {sk.get('best_usage', 'N/A')}\n\n"
            else:
                response += f"- Explanation: {sk.get('explanation', 'N/A')}\n- Hidden Interactions: {sk.get('hidden_interactions', 'N/A')}\n- Priority: {sk.get('priority', 'N/A')}\n- Combos: {sk.get('combos', 'N/A')}\n\n"

    stats = card.get('stats', {})
    response += (
        f"📊 **Stat Increments:**\n"
        f"• HP: {stats.get('hp', 'N/A')} | ATK: {stats.get('attack', 'N/A')} | DEF: {stats.get('defense', 'N/A')}\n"
        f"• Crit: {stats.get('crit', 'N/A')} | Block: {stats.get('block', 'N/A')} | Pierce: {stats.get('pierce', 'N/A')}\n\n"
        f"🎮 **PvP Analysis:** {card.get('analysis', {}).get('pvp', 'N/A')}\n"
        f"👹 **PvE Analysis:** {card.get('analysis', {}).get('pve', 'N/A')}\n"
        f"🏆 **Arena:** {card.get('analysis', {}).get('arena', 'N/A')}\n"
        f"👑 **Guild War:** {card.get('analysis', {}).get('guild_war', 'N/A')}\n\n"
        f"✅ **Strengths:** {card.get('strategy', {}).get('strengths', 'N/A')}\n"
        f"⚠️ **Weaknesses:** {card.get('strategy', {}).get('weaknesses', 'N/A')}\n\n"
        f"🆚 **Strong Against:** {', '.join(card.get('strategy', {}).get('strong_against', [])) if isinstance(card.get('strategy', {}).get('strong_against'), list) else card.get('strategy', {}).get('strong_against', 'N/A')}\n"
        f"❌ **Countered By:** {', '.join(card.get('strategy', {}).get('countered_by', [])) if isinstance(card.get('strategy', {}).get('countered_by'), list) else card.get('strategy', {}).get('countered_by', 'N/A')}\n\n"
        f"🔗 **Best Bonds:** {', '.join(card.get('recommendations', {}).get('bonds', [])) if isinstance(card.get('recommendations', {}).get('bonds'), list) else 'N/A'}\n"
        f"🎯 **Best Builds:**\n"
        f"- Main: {', '.join(card.get('recommendations', {}).get('team', [])) if isinstance(card.get('recommendations', {}).get('team'), list) else 'N/A'}\n"
        f"- Assist: {card.get('recommendations', {}).get('assist', 'N/A')}\n"
        f"- Guard: {card.get('recommendations', {}).get('guard', 'N/A')}\n\n"
        f"📊 **Final Rating:**\n"
        f"- Overall: {card.get('rating', {}).get('overall', 'N/A')}\n"
        f"- Investment Priority: {card.get('rating', {}).get('investment', 'N/A')}\n\n"
        f"💬 **Expert Opinion:**\n_{card.get('expert_opinion', 'N/A')}_"
    )
    return response

# AI Chat System
JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "Why don't skeletons fight each other? They don't have the guts.",
    "What do you call a fake noodle? An impasta!",
    "How does a penguin build its house? Igloos it together!",
    "Why was the math book sad? It had too many problems.",
    "What do you call a bear with no teeth? A gummy bear!",
    "How do you organize a space party? You planet.",
    "Why did the bicycle fall over? Because it was two-tired!",
    "What do you call cheese that isn't yours? Nacho cheese!",
    "Why do we tell actors to 'break a leg'? Because every play has a cast!",
    "Why did the coffee file a police report? It got mugged!",
    "What do you call a sleeping bull? A bulldozer!"
]

ANIME_RECS = {
    "shonen": [
        "**Bleach / Bleach: Thousand-Year Blood War**: A masterpiece of swords, soul reapers, and spectacular fights.",
        "**Jujutsu Kaisen**: Incredible animation, dark fantasy, and awesome power systems.",
        "**Hunter x Hunter (2011)**: Brilliant plot, depth of characters, and the best power system (Nen) in anime."
    ],
    "mystery": [
        "**Death Note**: A thrilling intellectual battle of minds between Light Yagami and L.",
        "**Monster**: A dark, slow-burn masterpiece about a neurosurgeon and a psychopathic mastermind.",
        "**Erased**: A gripping mystery involving time-travel, regret, and saving childhood friends."
    ],
    "slice of life": [
        "**Frieren: Beyond Journey's End**: A beautiful, emotional fantasy journey exploring what happens after the hero's party wins.",
        "**Your Lie in April**: A touching, musical drama that will pull your heartstrings.",
        "**Barakamon**: A delightful, lighthearted comedy about a calligrapher finding inspiration in a rural village."
    ]
}

MOVIE_RECS = {
    "sci-fi": [
        "**Interstellar**: A mind-bending space epic about love, time dilation, and survival.",
        "**Inception**: A brilliant heist thriller set inside the architecture of dreams.",
        "**Blade Runner 2048**: A stunning visual masterpiece exploring artificial life and identity."
    ],
    "action": [
        "**Mad Max: Fury Road**: Non-stop high-octane vehicular action in a gorgeous post-apocalyptic desert.",
        "**John Wick**: Slick, beautifully choreographed gun-fu action and world-building.",
        "**The Dark Knight**: The gold standard of superhero movies, featuring Heath Ledger's legendary Joker."
    ]
}

GAME_RECS = {
    "rpg": [
        "**The Witcher 3: Wild Hunt**: Rich storytelling, deep characters, and an expansive fantasy world.",
        "**Elden Ring**: A gorgeous, challenging open-world action RPG born from FromSoftware and George R.R. Martin.",
        "**Persona 5 Royal**: A stylish, turn-based JRPG blending high school life with dungeon crawling."
    ],
    "adventure": [
        "**The Legend of Zelda: Breath of the Wild**: Absolute freedom of exploration and dynamic interactions.",
        "**Red Dead Redemption 2**: An emotionally gripping western masterpiece with unmatched environmental detail."
    ]
}

def safe_math_eval(expression):
    # Allow alphabetic characters to support safe scientific function names like sqrt, sin, cos, pi, etc.
    cleaned = re.sub(r'[^a-zA-Z0-9+\-*/().\s]', '', expression)
    if not cleaned.strip():
        return None
    try:
        # Create a safe environment for evaluation
        allowed_names = {
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "pi": math.pi, "e": math.e, "log": math.log
        }
        val = eval(cleaned, {"__builtins__": {}}, allowed_names)
        return val
    except Exception:
        return None

def get_ai_response(query, chat_id=1, user_id=1):
    mem = get_memory(chat_id, user_id)
    query_lower = query.lower().strip()

    # Track user details if they introduce themselves
    name_match = re.search(r"(?:my name is|i am|call me)\s+([a-zA-Z0-9\s]+)", query_lower)
    if name_match:
        extracted_name = name_match.group(1).title().strip()
        mem["name"] = extracted_name
        response = f"Nice to meet you, {extracted_name}! I've stored that in my memory. What can I do for you today? 😊"
        mem["history"].append((query, response))
        return response

    fav_match = re.search(r"(?:my favorite character is|i love)\s+([a-zA-Z0-9\s]+)", query_lower)
    if fav_match:
        extracted_char = fav_match.group(1).title().strip()
        mem["favorite_char"] = extracted_char
        response = f"Oh, {extracted_char} is an amazing choice! I've noted that down. ⚔️"
        mem["history"].append((query, response))
        return response

    # Answer about stored details
    if "what's my name" in query_lower or "what is my name" in query_lower or "who am i" in query_lower:
        if mem["name"]:
            response = f"Your name is {mem['name']}! I'm happy to chat with you again. 😄"
        else:
            response = "Hmm, you haven't told me your name yet! What should I call you? 👤"
        mem["history"].append((query, response))
        return response

    if "favorite character" in query_lower or "who is my favorite" in query_lower:
        if mem["favorite_char"]:
            response = f"Your favorite character is {mem['favorite_char']}! Excellent taste."
        else:
            response = "You haven't told me your favorite character yet! Who is it? ⚔️"
        mem["history"].append((query, response))
        return response

    # 1. Math calculation
    is_math = ("solve" in query_lower or "calculate" in query_lower or "what is" in query_lower) and re.search(r'\d+', query_lower)
    if not is_math:
        is_math = any(op in query_lower for op in ["+", "-", "*", "/"]) and re.search(r'\d+', query_lower)

    if is_math:
        math_expr = query_lower.replace("solve", "").replace("calculate", "").replace("what is", "").replace("=", "").strip()
        val = safe_math_eval(math_expr)
        if val is not None:
            response = f"🧮 **Calculation:**\n`{math_expr}` = **{val}**"
            mem["history"].append((query, response))
            return response

    # 2. Programming / Coding help
    if "code" in query_lower or "program" in query_lower or "python" in query_lower or "function" in query_lower or "binary search" in query_lower or "recursion" in query_lower:
        if "binary search" in query_lower:
            response = (
                "💻 **Binary Search in Python:**\n\n"
                "Here is a classic iterative binary search implementation:\n"
                "```python\n"
                "def binary_search(arr, target):\n"
                "    low, high = 0, len(arr) - 1\n"
                "    while low <= high:\n"
                "        mid = (low + high) // 2\n"
                "        if arr[mid] == target:\n"
                "            return mid\n"
                "        elif arr[mid] < target:\n"
                "            low = mid + 1\n"
                "        else:\n"
                "            high = mid - 1\n"
                "    return -1\n"
                "```\n"
                "**Explanation:** It splits the search space in half with every step, achieving a highly efficient **O(log N)** time complexity! Let me know if you need help with any other algorithms."
            )
        else:
            response = (
                "💻 **Programming Help:**\n\n"
                "I'd love to help you with programming! Whether it's Python, Javascript, databases, or algorithms, just ask. Here is a handy Python template to get started:\n"
                "```python\n"
                "def greet_user(name):\n"
                "    return f'Hello, {name}! Let\\'s build something incredible!'\n"
                "```\n"
                "What specific coding question or language are we working on?"
            )
        mem["history"].append((query, response))
        return response

    # 3. Translation
    if "translate" in query_lower:
        target = 'tr' if 'turkish' in query_lower or 'tur' in query_lower else 'en'
        phrase = query_lower.replace("translate", "").replace("to turkish", "").replace("to english", "").strip()
        if not phrase:
            phrase = "Hello, how can I assist you today?"
        try:
            trans = GoogleTranslator(source='auto', target=target).translate(phrase)
            lang_name = "🇹🇷 Turkish" if target == 'tr' else "🇬🇧 English"
            response = f"🌎 **Translation to {lang_name}:**\n\n_{trans}_"
        except Exception:
            response = "❌ Translation service is currently taking a break. Let's try again shortly!"
        mem["history"].append((query, response))
        return response

    # 4. Summarization
    if "summarize" in query_lower:
        text_to_sum = query.replace("summarize", "").replace("Summarize", "").strip()
        if len(text_to_sum) < 20:
            response = "Sure! Please provide a longer block of text (at least a paragraph) so I can create a meaningful summary for you."
        else:
            sentences = [s.strip() for s in text_to_sum.split('.') if s.strip()]
            summary_sentences = sentences[:min(3, len(sentences))]
            response = "📝 **Text Summary:**\n\n" + ". ".join(summary_sentences) + "."
        mem["history"].append((query, response))
        return response

    # 5. Tell jokes
    if "joke" in query_lower or "funny" in query_lower:
        joke = random.choice(JOKES)
        response = f"😄 Here's a joke for you:\n\n_{joke}_"
        mem["history"].append((query, response))
        return response

    # 6. Recommendations
    if "recommend" in query_lower or "suggestion" in query_lower:
        if "movie" in query_lower:
            genre = "sci-fi" if "sci-fi" in query_lower or "science" in query_lower else "action"
            rec = random.choice(MOVIE_RECS[genre])
            response = f"🎬 **Movie Recommendation ({genre.upper()}):**\n\n{rec}\n\nI hope you enjoy it! Let me know if you want another category."
        elif "anime" in query_lower:
            genre = "shonen" if "shonen" in query_lower or "fight" in query_lower or "bleach" in query_lower else "mystery"
            rec = random.choice(ANIME_RECS[genre])
            response = f"🌸 **Anime Recommendation ({genre.upper()}):**\n\n{rec}\n\nAnime is a beautiful medium. Enjoy the watch!"
        else:
            rec = random.choice(GAME_RECS["rpg"])
            response = f"🎮 **Game Recommendation:**\n\n{rec}\n\nIf you love deep systems and immersive worlds, this is perfect."
        mem["history"].append((query, response))
        return response

    # 7. Bleach Specific questions matching database dynamically
    for key in list(data_manager.get_collection("characters").keys()):
        if key.replace("_", " ") in query_lower:
            response = get_build_response(key)
            mem["history"].append((query, response))
            return response

    # Fallback to general keyword match
    for key, value in GENERAL_KNOWLEDGE.items():
        if key in query_lower:
            mem["history"].append((query, value))
            return value

    # Have Bleach as an area of expertise, but answer normally (Requirement 1)
    greetings = ["hello", "hi", "hey", "greetings", "yo", "sup"]
    if any(g in query_lower.split() for g in greetings):
        welcome_msg = "Hello there! I'm your friendly AI assistant. I'm here to chat, answer general knowledge, tell jokes, solve math, assist with programming, and yes—I also have deep expertise in Bleach Mobile 3D! How is your day going? 😊"
        mem["history"].append((query, welcome_msg))
        return welcome_msg

    how_are_you = ["how are you", "how's it going", "how is it going", "how you doing"]
    if any(hay in query_lower for hay in how_are_you):
        response = "I'm doing absolutely wonderful, thank you for asking! I'm here and ready to help you with anything. How about you? How has your week been? 🌟"
        mem["history"].append((query, response))
        return response

    help_terms = ["help", "what can you do", "commands", "features"]
    if any(ht in query_lower.split() for ht in help_terms):
        response = "I can do so many things! We can have a natural conversation, I can answer general knowledge questions, explain complex concepts, solve math, write code, tell jokes, give movie/anime/game recommendations, and translate text. Plus, I can give expert build guides for Bleach Mobile 3D characters. Let's get started!"
        mem["history"].append((query, response))
        return response

    # Context continuation fallback
    if mem["history"]:
        last_user, last_bot = mem["history"][-1]
        response = f"That is really interesting! Regarding what we were discussing previously, I'd love to chat more. Tell me, do you have any other questions about that, or should we talk about something else? I'm all ears! 👂"
    else:
        response = "I'm completely here for you! Ask me anything—from daily life advice, concepts, programming help, jokes, or even Bleach Mobile 3D guides. Let's make today productive and fun! 🚀"

    mem["history"].append((query, response))
    return response
