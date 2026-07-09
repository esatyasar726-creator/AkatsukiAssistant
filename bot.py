import os
import asyncio
import logging
import random
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
from banner_data import BANNERS, REFERENCE_DATE, REFERENCE_DAY
from database import (
    init_db, update_score, get_user_score, get_leaderboard,
    add_chat_member, remove_chat_member, get_chat_members,
    set_reminder_enabled, set_reminder_lead, get_reminder_settings,
    get_all_chats_with_reminders, get_user_profile, add_rewards,
    claim_daily, get_coins_leaderboard, unlock_achievement,
    get_or_create_daily_quest, progress_daily_quest, claim_daily_quest_rewards,
    set_admin_setting, get_admin_setting, add_to_inventory, get_inventory
)
from game_manager import game_manager
from game_logic import get_build_response, get_card_analysis, get_ai_response
from data_manager import data_manager
from formatters import format_card_info, format_character_info, format_meta
from telegram import Update, ChatMember, ChatMemberUpdated
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ChatMemberHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")

RULES = """
📜 AKATSUKI CLAN RULES

1. Respect every member regardless of their language or country.
2. Everyone is free to speak their own language.
3. No insults, hate speech, racism or harassment.
4. No spam, scams or advertising.
5. Participate in clan events whenever possible.
6. Follow instructions from the Leader, Vice Leader and Admins.
7. Help each other and enjoy the game.

⚔ Respect • Loyalty • Teamwork
"""

LEADERS = """
👑 AKATSUKI STAFF

🏛 Leader
Klaus

🥈 Vice Leaders
Asta & YurtSever

🛡 Admins
BabaYaga & Jaco Tenma
"""

HELP = """
🤖 AKATSUKI CLAN ASSISTANT

Available Commands

⚔️ GAME GUIDES & DATABASE
/character <name>  - View character's skills, type & lore
/build <character> - View extremely detailed builds & analysis
/bonds <character> - View ALL Attack, HP, and Defense bonds
/cardinfo <card>   - View full card analysis, rating & skills
/assist <name>     - View assist skill & recommendations
/guard <name>      - View guard skill & recommendations
/compare <c1> vs <c2> - Compare two characters side-by-side
/meta              - View the current meta & tier lists
/tierlist          - Shortcut to view character tier lists
/events            - View Ankara & GMT event schedules
/event             - View latest server rotations & events
/news              - View the latest clan news & events
/banner            - View active banner for server day
/nextbanner        - View the upcoming banner release info

🤖 ADVANCED AI CHAT
/ask <your question> - Have a friendly conversation, solve math, write code, get jokes, recommendations, or translations!

🎯 DAILY QUESTS & REWARDS
/quest             - View your active randomized Daily Quest!
/claimquest        - Claim rewards for completed Daily Quests!
/daily             - Claim your daily Coins & streak bonus!
/profile           - View your level, rank, XP, and achievements!
/inventory         - View your Gacha character collection!

🎪 GACHA SIMULATOR
/gacha             - Perform a single premium character summon!
/gacha10           - Perform a 10x multi character summon!

🎮 MULTIPLAYER GAMES
/games        - View available games and their rules
/play <game>  - Open a game lobby (Trivia, Scramble, Blackjack, Mines, Hangman)
/join         - Join the active game lobby in the chat
/startgame    - Start the joined game lobby!
/reminder [on|off|status|15|30|60] - Manage chat reminders (Admin only)
"""

# Admin list for panel commands
ADMIN_IDS = [123456789, 987654321]  # Mock admin lists, Klaus & staff IDs can be added

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚔ Welcome to Akatsuki Assistant!\n\nUse /help to see all commands.", parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP)

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(RULES)

async def leaders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(LEADERS)

def get_current_day():
    ref_date = datetime.strptime(REFERENCE_DATE, "%Y-%m-%d")
    today = datetime.utcnow()
    delta_days = (today - ref_date).days
    return REFERENCE_DAY + delta_days

async def banner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 1:
        try:
            day = int(context.args[0])
        except ValueError:
            await update.message.reply_text("Usage: /banner <day>")
            return
    else:
        day = get_current_day()

    # Check for admin custom banner overrides
    custom_banner = get_admin_setting(f"banner_day_{day}")
    if custom_banner:
        await update.message.reply_text(f"📅 Current Override Banner (Day {day})\n\nDay {day}: {custom_banner}")
        return

    active_day = None
    sorted_days = sorted(BANNERS.keys())
    for d in sorted_days:
        if d <= day:
            active_day = d
        else:
            break

    if active_day:
        await update.message.reply_text(f"📅 Current Banner (Day {day})\n\nDay {active_day}: {BANNERS[active_day]}")
    else:
        await update.message.reply_text("❌ No active banner found for the current day.")

async def next_banner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day = get_current_day()
    sorted_days = sorted(BANNERS.keys())

    next_day = None
    for d in sorted_days:
        if d > day:
            next_day = d
            break

    if next_day:
        ref_date = datetime.strptime(REFERENCE_DATE, "%Y-%m-%d")
        days_until = next_day - REFERENCE_DAY
        banner_date = ref_date + timedelta(days=days_until)
        date_str = banner_date.strftime("%d %B %Y")

        await update.message.reply_text(
            f"⏭ Next Banner\n\n"
            f"Upcoming: {BANNERS[next_day]}\n"
            f"Day: {next_day}\n"
            f"Release Date: {date_str}"
        )
    else:
        await update.message.reply_text("❌ No upcoming banners found in the schedule.")

async def events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Dynamic events fetch with potential admin custom overrides
    custom_sched = get_admin_setting("custom_schedule")
    if custom_sched:
        await update.message.reply_text(f"📅 **CLAN EVENTS SCHEDULE (ADMIN OVERRIDE)**\n\n{custom_sched}", parse_mode="Markdown")
        return

    events_text = (
        "📅 CLAN EVENTS SCHEDULE\n\n"
        "⚔ Clan War\n"
        "Saturday 10:00 AM (Istanbul GMT+3)\n"
        "Saturday 07:00 AM (GMT)\n\n"
        "🔮 Inner\n"
        "12:30 PM-01:00 PM, 08:30 PM-09:00 PM (Istanbul GMT+3)\n"
        "09:30 AM-10:00 AM, 05:30 PM-06:00 PM (GMT)\n\n"
        "🏆 Top Vs\n"
        "12:00 PM-02:00 PM, 08:00 PM-10:00 PM (Istanbul GMT+3)\n"
        "09:00 AM-11:00 AM, 05:00 PM-07:00 PM (GMT)\n\n"
        "🏰 Las Noches\n"
        "02:00 PM, 04:00 PM, 06:00 PM, 10:00 PM, 11:00 PM (Istanbul GMT+3)\n"
        "11:00 AM, 01:00 PM, 03:00 PM, 07:00 PM, 08:00 PM (GMT)"
    )
    await update.message.reply_text(events_text)

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("Lütfen çevirmek istediğin mesaja yanıt ver.")
        return

    text_to_translate = update.message.reply_to_message.text or update.message.reply_to_message.caption
    if not text_to_translate:
        await update.message.reply_text("❌ Mesaj içeriği bulunamadı.")
        return

    try:
        translated_en = GoogleTranslator(source='auto', target='en').translate(text_to_translate)
        translated_tr = GoogleTranslator(source='auto', target='tr').translate(text_to_translate)

        response = (
            f"🇬🇧 Eng:\n{translated_en}\n\n"
            f"🇹🇷 Tur:\n{translated_tr}"
        )
        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Translation error: {e}")
        await update.message.reply_text("❌ Çeviri yapılırken bir hata oluştu.")

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    p = get_user_profile(user_id)
    pts = p['score'] if p else 0
    await update.message.reply_text(f"👤 {username}, your total score is: {pts} points.")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_users = get_leaderboard()
    if not top_users:
        await update.message.reply_text("The leaderboard is currently empty.")
        return

    text = "🏆 AKATSUKI TOP 10 SCORE LEADERBOARD\n\n"
    for i, (username, pts) in enumerate(top_users, 1):
        text += f"{i}. {username or 'Unknown'}: {pts} pts\n"

    coins_lead = get_coins_leaderboard(5)
    if coins_lead:
        text += "\n🪙 COIN BILLIONAIRES LEADERBOARD\n"
        for i, (username, coins) in enumerate(coins_lead, 1):
            text += f"{i}. {username or 'Unknown'}: {coins} 🪙\n"

    await update.message.reply_text(text)

async def math_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    msg = game_manager.start_lobby(chat_id, "scramble", mode="solo")
    await update.message.reply_text(msg, parse_mode="Markdown")

async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = update.chat_member
    chat_id = result.chat.id
    user_id = result.from_user.id
    username = result.from_user.username or result.from_user.first_name

    was_member = result.old_chat_member.status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ]
    is_member = result.new_chat_member.status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ]

    if not was_member and is_member:
        add_chat_member(chat_id, user_id, username)
    elif was_member and not is_member:
        remove_chat_member(chat_id, user_id)

EVENT_SCHEDULE = [
    (5, 10, 0, "Clan War"),
    (0, 12, 30, "Inner"), (1, 12, 30, "Inner"), (2, 12, 30, "Inner"), (3, 12, 30, "Inner"), (4, 12, 30, "Inner"), (5, 12, 30, "Inner"), (6, 12, 30, "Inner"),
    (0, 20, 30, "Inner"), (1, 20, 30, "Inner"), (2, 20, 30, "Inner"), (3, 20, 30, "Inner"), (4, 20, 30, "Inner"), (5, 20, 30, "Inner"), (6, 20, 30, "Inner"),
    (0, 12, 0, "Top VS"), (1, 12, 0, "Top VS"), (2, 12, 0, "Top VS"), (3, 12, 0, "Top VS"), (4, 12, 0, "Top VS"), (5, 12, 0, "Top VS"), (6, 12, 0, "Top VS"),
    (0, 20, 0, "Top VS"), (1, 20, 0, "Top VS"), (2, 20, 0, "Top VS"), (3, 20, 0, "Top VS"), (4, 20, 0, "Top VS"), (5, 20, 0, "Top VS"), (6, 20, 0, "Top VS"),
    (0, 14, 0, "Las Noches"), (1, 14, 0, "Las Noches"), (2, 14, 0, "Las Noches"), (3, 14, 0, "Las Noches"), (4, 14, 0, "Las Noches"), (5, 14, 0, "Las Noches"), (6, 14, 0, "Las Noches"),
    (0, 16, 0, "Las Noches"), (1, 16, 0, "Las Noches"), (2, 16, 0, "Las Noches"), (3, 16, 0, "Las Noches"), (4, 16, 0, "Las Noches"), (5, 16, 0, "Las Noches"), (6, 16, 0, "Las Noches"),
    (0, 18, 0, "Las Noches"), (1, 18, 0, "Las Noches"), (2, 18, 0, "Las Noches"), (3, 18, 0, "Las Noches"), (4, 18, 0, "Las Noches"), (5, 18, 0, "Las Noches"), (6, 18, 0, "Las Noches"),
    (0, 22, 0, "Las Noches"), (1, 22, 0, "Las Noches"), (2, 22, 0, "Las Noches"), (3, 22, 0, "Las Noches"), (4, 22, 0, "Las Noches"), (5, 22, 0, "Las Noches"), (6, 22, 0, "Las Noches"),
    (0, 23, 0, "Las Noches"), (1, 23, 0, "Las Noches"), (2, 23, 0, "Las Noches"), (3, 23, 0, "Las Noches"), (4, 23, 0, "Las Noches"), (5, 23, 0, "Las Noches"), (6, 23, 0, "Las Noches"),
]

async def check_events(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.utcnow() + timedelta(hours=3)
    current_day = now.weekday()

    chats = get_all_chats_with_reminders()
    for chat_id, lead_minutes in chats:
        for event_day, event_hour, event_minute, event_name in EVENT_SCHEDULE:
            event_time = now.replace(hour=event_hour, minute=event_minute, second=0, microsecond=0)
            if event_day != current_day:
                continue

            reminder_time = event_time - timedelta(minutes=lead_minutes)
            if now.hour == reminder_time.hour and now.minute == reminder_time.minute:
                members = get_chat_members(chat_id)
                if not members:
                    continue

                mentions = [f"@{m[1]}" for m in members if m[1]]
                chunk_size = 50
                for i in range(0, len(mentions), chunk_size):
                    chunk = mentions[i:i + chunk_size]
                    msg = ""
                    if i == 0:
                        msg = (
                            f"⏰ EVENT REMINDER\n\n"
                            f"Only **{lead_minutes} minutes** left until **{event_name}** starts!\n\n"
                            f"Get your team ready!\n\n"
                        )
                    msg += " ".join(chunk)
                    try:
                        await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")
                    except Exception as e:
                        logging.error(f"Failed to send reminder to {chat_id}: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    text = update.message.text.lower().strip()

    if 'math_answers' in context.bot_data and chat_id in context.bot_data['math_answers']:
        correct_answer = context.bot_data['math_answers'][chat_id]
        try:
            if int(text) == correct_answer:
                new_score = update_score(user_id, username, 10)
                del context.bot_data['math_answers'][chat_id]

                # Progress math quest
                was_com = progress_daily_quest(user_id, "math")
                add_rewards(user_id, username, 20, 40, won=True)

                reply_text = f"✅ Correct! {username} earned 10 points! Total: {new_score}"
                if was_com:
                    reply_text += "\n\n🎯 **DAILY QUEST COMPLETED!** Use `/quest` to claim!"
                await update.message.reply_text(reply_text)
                return
        except ValueError:
            pass

    # Check active games
    game_res = game_manager.handle_lobby_answer(chat_id, user_id, text)
    if game_res:
        leveled_up, lvl, rank = add_rewards(user_id, username, game_res['coins'], game_res['xp'], won=True)

        # Progress play quest
        was_com = progress_daily_quest(user_id, "play")

        reply_text = game_res['msg']
        if was_com:
            reply_text += "\n\n🎯 **DAILY QUEST COMPLETED!** Use `/quest` to claim!"
        if leveled_up:
            reply_text += f"\n\n⚡ **LEVEL UP!** **{username}** reached Level **{lvl}** ({rank})! 👑"
            unlock_achievement(user_id, "Rank Master")

        await update.message.reply_text(reply_text, parse_mode="Markdown")
        return

async def dice_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    msg = game_manager.start_dice_game(chat_id)
    await update.message.reply_text(msg)

    await asyncio.sleep(30)

    result = game_manager.resolve_dice_game(chat_id)
    if not result:
        return

    if isinstance(result, str):
        await context.bot.send_message(chat_id=chat_id, text=result)
        return

    results, winner_id, winner_name = result
    add_rewards(winner_id, winner_name, 50, 100, won=True)
    new_score = update_score(winner_id, winner_name, 20)

    # Progress play quest for all participants
    lobby = game_manager.active_games.get(chat_id)
    if lobby:
        for p_id in lobby.get('players', {}):
            progress_daily_quest(p_id, "play")

    res_text = "🎲 DICE GAME RESULTS:\n" + "\n".join(results)
    res_text += f"\n\n🏆 Winner: {winner_name} (+50 Coins, +100 XP)! Total legacy score: {new_score}"
    await context.bot.send_message(chat_id=chat_id, text=res_text)

async def join_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    success, res = game_manager.join_lobby(chat_id, user_id, username)
    if success:
        await update.message.reply_text(res, parse_mode="Markdown")
        return

    if game_manager.join_dice_game(chat_id, user_id, username):
        await update.message.reply_text(f"✅ {username} joined the dice game!")
    else:
        await update.message.reply_text("❌ No game lobby to join or you are already in.")

async def emoji_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emoji, answer = game_manager.start_emoji_guess()
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"🧩 **Emoji Scramble Guess!**\n\nWhat is the name of this object/animal: {emoji}?\n\nUnscramble/guess directly by typing it!")

async def quiz_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    msg = game_manager.start_lobby(chat_id, "trivia", mode="multiplayer", max_players=5)
    await update.message.reply_text(msg, parse_mode="Markdown")

async def build_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Please specify a character name! Example: `/build SP Aizen`", parse_mode="Markdown")
        return

    user_id = update.effective_user.id
    query = " ".join(context.args)
    response = get_build_response(query)

    # Progress build quest
    was_com = progress_daily_quest(user_id, "build")
    if was_com:
        response += "\n\n🎯 **DAILY QUEST COMPLETED!** Use `/quest` to claim!"

    await update.message.reply_text(response, parse_mode="Markdown")

async def card_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Please specify a card name! Example: `/cardinfo Final Fusion`", parse_mode="Markdown")
        return

    query = " ".join(context.args)
    response = get_card_analysis(query)
    await update.message.reply_text(response, parse_mode="Markdown")

async def update_db_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    import data_updater
    data_updater.update_database()
    data_manager.reload()
    await update.message.reply_text("🔄 **Database updated & reloaded successfully from External Spreadsheet!**", parse_mode="Markdown")

async def character_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Please specify a character name! Example: `/character resurrection barragan`", parse_mode="Markdown")
        return

    query = " ".join(context.args)
    char = data_manager.find_item("characters", query)
    if not char:
        await update.message.reply_text("❌ Character not found in our database.")
        return

    response = format_character_info(char)
    await update.message.reply_text(response, parse_mode="Markdown")

async def assist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Please specify a character name! Example: `/assist SP Aizen`", parse_mode="Markdown")
        return

    query = " ".join(context.args)
    char = data_manager.find_item("characters", query)
    if not char:
        await update.message.reply_text("❌ Character not found in our database.")
        return

    build = char.get("build", {})
    assists = build.get("assists", [])

    res = (
        f"👥 **ASSIST RECOMMENDATIONS FOR {char['name'].upper()}** 👥\n\n"
        f"**Highly Recommended Assists:**\n" + "\n".join([f"• {a}" for a in assists]) + "\n\n"
        f"⚡ **Assist Skill Details:**\n"
        f"_{char.get('skills', {}).get('Assist', 'N/A')}_\n\n"
        f"💡 **Synergy Tips:** Combine with defense reduction or high-damage main characters."
    )
    await update.message.reply_text(res, parse_mode="Markdown")

async def guard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Please specify a character name! Example: `/guard SP Aizen`", parse_mode="Markdown")
        return

    query = " ".join(context.args)
    char = data_manager.find_item("characters", query)
    if not char:
        await update.message.reply_text("❌ Character not found in our database.")
        return

    build = char.get("build", {})
    guards = build.get("guards", [])

    res = (
        f"🛡️ **GUARD RECOMMENDATIONS FOR {char['name'].upper()}** 🛡️\n\n"
        f"**Highly Recommended Guards:**\n" + "\n".join([f"• {g}" for g in guards]) + "\n\n"
        f"⚡ **Guard Skill Details:**\n"
        f"_{char.get('skills', {}).get('Guard', 'N/A')}_\n\n"
        f"💡 **Gameplay:** Guards trigger automatic protection when your HP falls below the critical threshold."
    )
    await update.message.reply_text(res, parse_mode="Markdown")

async def bonds_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /bonds <character name>")
        return
    query = " ".join(context.args)
    char = data_manager.find_item("characters", query)
    if char:
        b = char['bonds']
        res = (
            f"🔗 **ALL RECOMMENDED BONDS FOR {char['name'].upper()}** 🔗\n\n"
            f"⚔️ **ALL Recommended Attack Bonds**\n" + "\n".join([f"- {x}" for x in b.get('attack', [])]) + "\n\n"
            f"❤️ **ALL Recommended HP Bonds**\n" + "\n".join([f"- {x}" for x in b.get('hp', [])]) + "\n\n"
            f"🛡️ **ALL Recommended Defense/Armor Bonds**\n" + "\n".join([f"- {x}" for x in b.get('defense', [])])
        )
        await update.message.reply_text(res, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Character not found.")

async def meta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    meta_data = data_manager.get_meta()
    response = format_meta(meta_data)

    # Progress meta quest
    was_com = progress_daily_quest(user_id, "meta")
    if was_com:
        response += "\n\n🎯 **DAILY QUEST COMPLETED!** Use `/quest` to claim!"

    await update.message.reply_text(response, parse_mode="Markdown")

async def event_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    events_data = data_manager.get_events()
    res = "📅 **EVENTS & ROTATIONS**\n\n"
    res += f"📰 **News:** {events_data.get('news', 'No current news.')}\n\n"
    res += f"⚔️ **Weekly:** {', '.join(events_data.get('weekly_events', []))}\n\n"
    rot = events_data.get('rotation', {})
    for k, v in rot.items():
        res += f"🔄 **{k.replace('_', ' ').title()}:** Cycles every {v['cycle']} days. Items: {', '.join(v['items'])}\n"
    await update.message.reply_text(res, parse_mode="Markdown")

async def shop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = (
        "🛒 **SHOP VALUE & ANALYSIS** 🛒\n\n"
        "• **Crystal Exchange:** Always buy Stamina & SP Character Shards. 💎\n"
        "• **Gacha Shop:** Save for full Weapon Selectors. ⚔️\n"
        "• **Seireitei Shop:** Prioritize Orange Accessories.\n\n"
        "💬 *Shop rotations cycle every 7 days. Spend wisely!*"
    )
    await update.message.reply_text(res, parse_mode="Markdown")

async def banner_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = (
        "📜 **BANNER HISTORY ANALYSIS** 📜\n\n"
        "• Day 1-14: Ichigo (Bankai)\n"
        "• Day 28: Kenpachi Zaraki\n"
        "• Day 120: Tensa Zangetsu\n"
        "• Day 280: SP Sosuke Aizen\n\n"
        "Use `/banner` to check what's currently active!"
    )
    await update.message.reply_text(res, parse_mode="Markdown")

async def compare_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or "vs" not in " ".join(context.args).lower():
        await update.message.reply_text("Usage: `/compare <char1> vs <char2>`\nExample: `/compare SP Aizen vs Byakuya`", parse_mode="Markdown")
        return

    raw_query = " ".join(context.args)
    parts = raw_query.lower().split("vs")
    if len(parts) < 2:
        await update.message.reply_text("Usage: `/compare <char1> vs <char2>`")
        return

    c1_query = parts[0].strip()
    c2_query = parts[1].strip()

    char1 = data_manager.find_item("characters", c1_query)
    char2 = data_manager.find_item("characters", c2_query)

    if not char1 or not char2:
        await update.message.reply_text(f"❌ One or both characters not found.\n• Found '{c1_query}': {'✅' if char1 else '❌'}\n• Found '{c2_query}': {'✅' if char2 else '❌'}")
        return

    b1 = char1.get("build", {})
    b2 = char2.get("build", {})

    comparison = (
        f"⚖️ **SIDE-BY-SIDE COMPARISON** ⚖️\n\n"
        f"⚔️ **{char1['name'].upper()}**  *VS*  **{char2['name'].upper()}**\n\n"
        f"• **Rarity / Type:**\n  - {char1['name']}: {char1.get('type', 'N/A')}\n  - {char2['name']}: {char2.get('type', 'N/A')}\n\n"
        f"• **PvP Arena Rating:**\n  - {char1['name']}: **{b1.get('pvp_rating', 'N/A')}**\n  - {char2['name']}: **{b2.get('pvp_rating', 'N/A')}**\n\n"
        f"• **PvE Boss Rating:**\n  - {char1['name']}: **{b1.get('pve_rating', 'N/A')}**\n  - {char2['name']}: **{b2.get('pve_rating', 'N/A')}**\n\n"
        f"• **Investment Level:**\n  - {char1['name']}: {b1.get('investment', 'N/A')}\n  - {char2['name']}: {b2.get('investment', 'N/A')}\n\n"
        f"💡 **Synergies:**\n  - {char1['name']}: {', '.join(b1.get('synergies', []))}\n  - {char2['name']}: {', '.join(b2.get('synergies', []))}"
    )
    await update.message.reply_text(comparison, parse_mode="Markdown")

async def tierlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await meta_command(update, context)

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Dynamic news with potential custom admin override announcements
    custom_news = get_admin_setting("clan_announcement")
    if custom_news:
        await update.message.reply_text(f"📢 **LATEST CLAN ANNOUNCEMENT (ADMIN)**\n\n{custom_news}", parse_mode="Markdown")
        return
    await event_command(update, context)

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /ask <your question>")
        return
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    query = " ".join(context.args)

    response = get_ai_response(query, chat_id, user_id)

    # Check math progression quest
    if "🧮 **Calculation:**" in response:
        was_com = progress_daily_quest(user_id, "math")
        if was_com:
            response += "\n\n🎯 **DAILY QUEST COMPLETED!** Use `/quest` to claim!"

    await update.message.reply_text(response, parse_mode="Markdown")

async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    success, res_msg = claim_daily(user_id, username)
    if success:
        unlock_achievement(user_id, "First Step")
    await update.message.reply_text(res_msg, parse_mode="Markdown")

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name
    p = get_user_profile(user_id)
    if not p:
        add_rewards(user_id, username, 0, 10, won=False)
        p = get_user_profile(user_id)

    win_rate = (p['games_won'] / p['games_played'] * 100) if p['games_played'] > 0 else 0.0

    profile_text = (
        f"👤 **SOUL REAPER PROFILE: {username.upper()}** 👤\n\n"
        f"🏅 **Rank:** `{p['rank']}` (Level {p['level']})\n"
        f"⚡ **XP:** `{p['xp']} / {p['level'] * 150}`\n"
        f"🪙 **Coins:** `{p['coins']} Coins` 🪙\n"
        f"🏆 **Legacy Score:** `{p['score']} pts`\n\n"
        f"📊 **GAMEPLAY STATISTICS:**\n"
        f"• Games Played: `{p['games_played']}`\n"
        f"• Games Won: `{p['games_won']}`\n"
        f"• Win Rate: `{win_rate:.1f}%`\n"
        f"• Active Win Streak: `{p['win_streak']} games` 🔥\n"
        f"• Daily Claim Streak: `{p['daily_streak']} days`\n\n"
        f"🏆 **UNLOCKED ACHIEVEMENTS:**\n" + (", ".join([f"🏅 `{a}`" for a in p['achievements']]) if p['achievements'] else "No achievements unlocked yet.")
    )
    await update.message.reply_text(profile_text, parse_mode="Markdown")

# --- NEW: Daily Quest Bot Commands ---
async def quest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    q = get_or_create_daily_quest(user_id)

    status_emoji = "⏳ In Progress"
    if q["completed"] == 1:
        status_emoji = "✅ Completed! Use `/claimquest` to claim your rewards!"
    elif q["completed"] == 2:
        status_emoji = "🎁 Claimed & Redeemed"

    res = (
        f"📋 **DAILY ACTIVE QUEST FOR {username.upper()}** 📋\n\n"
        f"🎯 **Quest:** {q['name']}\n"
        f"📊 **Progress:** `{q['progress']} / {q['target']}`\n"
        f"🏅 **Status:** {status_emoji}\n\n"
        f"🪙 **Rewards:** **{q['reward_coins']} Coins** & **{q['reward_xp']} XP**!\n\n"
        f"💡 *Quests reset automatically every day at midnight GMT!*"
    )
    await update.message.reply_text(res, parse_mode="Markdown")

async def claim_quest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    rewards = claim_daily_quest_rewards(user_id, username)
    if rewards:
        coins, xp = rewards
        await update.message.reply_text(
            f"🎉 **Quest Claimed successfully!**\n\n"
            f"Earned: **{coins} Coins** 🪙 & **{xp} XP** ⚡\n"
            f"Your Soul Reaper profile has been updated!", parse_mode="Markdown"
        )
    else:
        q = get_or_create_daily_quest(user_id)
        if q["completed"] == 2:
            await update.message.reply_text("❌ You have already claimed today's quest rewards!")
        else:
            await update.message.reply_text(f"⏳ Your daily quest is not completed yet!\nProgress: `{q['progress']}/{q['target']}`")

# --- NEW: Admin Panel Settings Commands ---
async def admin_setnews_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        # Check if chat admin if not in mock owner list
        member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        if member.status not in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            await update.message.reply_text("❌ Administrative privilege required to perform this action.")
            return

    if not context.args:
        await update.message.reply_text("Usage: `/admin_setnews <text>`", parse_mode="Markdown")
        return

    text = " ".join(context.args)
    set_admin_setting("clan_announcement", text)
    await update.message.reply_text("✅ **Successfully updated official Clan Announcement/News!**", parse_mode="Markdown")

async def admin_setbanner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        if member.status not in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            await update.message.reply_text("❌ Administrative privilege required to perform this action.")
            return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: `/admin_setbanner <server_day> <banner_text>`", parse_mode="Markdown")
        return

    day_str = context.args[0]
    banner_text = " ".join(context.args[1:])
    set_admin_setting(f"banner_day_{day_str}", banner_text)
    await update.message.reply_text(f"✅ **Successfully overridden Banner for Day {day_str}!**", parse_mode="Markdown")

async def admin_setevent_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        member = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        if member.status not in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            await update.message.reply_text("❌ Administrative privilege required to perform this action.")
            return

    if not context.args:
        await update.message.reply_text("Usage: `/admin_setevent <custom_schedule_text>`", parse_mode="Markdown")
        return

    sched_text = " ".join(context.args)
    set_admin_setting("custom_schedule", sched_text)
    await update.message.reply_text("✅ **Successfully updated official Custom Event Schedule!**", parse_mode="Markdown")

# --- NEW: Gacha Character Summon Simulator ---
async def gacha_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    # Rate definitions: SP (1.5%), SSR (5.0%), SR (20%), R (73.5%)
    r = random.random() * 100
    if r <= 1.5:
        rarity = "SP"
        pool = ["sp___sosuke_aizen", "final_fusion___sosuke_aizen_ffa"]
    elif r <= 6.5:
        rarity = "SSR"
        pool = ["demon_byakuya_kuchiki", "sp_byakuya_kuchiki", "demon_fox_gin_ichimaru_fox_gin"]
    elif r <= 26.5:
        rarity = "SR"
        pool = ["coco_byakuya_kuchiki", "coco_gin_ichimaru", "halloween_gin_ichimaru_fox_gin"]
    else:
        rarity = "R"
        pool = ["resurrection_barragan_bara_v2", "coco_grimmjow"]

    char_key = random.choice(pool)
    char_data = data_manager.find_item("characters", char_key)
    char_name = char_data["name"] if char_data else char_key.replace("_", " ").title()

    # Track in database inventory
    add_to_inventory(user_id, char_key, char_name, rarity)

    # Progress gacha quest
    was_com = progress_daily_quest(user_id, "gacha")

    # Reward XP for summoning
    add_rewards(user_id, username, 10, 20)

    # Frame gacha output beautifully
    stars = "⭐" * (5 if rarity in ["SP", "SSR"] else 3)
    res = (
        f"🎪 **GACHA PREMIUM SUMMON** 🎪\n\n"
        f"💫 **You pulled:** `{char_name}`\n"
        f"🏅 **Rarity:** **[{rarity}]** {stars}\n\n"
        f"✨ Saved to your dynamic profile inventory! Use `/inventory` to check your collection!"
    )
    if was_com:
        res += "\n\n🎯 **DAILY QUEST COMPLETED!** Use `/quest` to claim!"

    await update.message.reply_text(res, parse_mode="Markdown")

async def gacha10_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    pulls = []
    for _ in range(10):
        r = random.random() * 100
        if r <= 1.5:
            rarity = "SP"
            pool = ["sp___sosuke_aizen", "final_fusion___sosuke_aizen_ffa"]
        elif r <= 6.5:
            rarity = "SSR"
            pool = ["demon_byakuya_kuchiki", "sp_byakuya_kuchiki", "demon_fox_gin_ichimaru_fox_gin"]
        elif r <= 26.5:
            rarity = "SR"
            pool = ["coco_byakuya_kuchiki", "coco_gin_ichimaru", "halloween_gin_ichimaru_fox_gin"]
        else:
            rarity = "R"
            pool = ["resurrection_barragan_bara_v2", "coco_grimmjow"]

        char_key = random.choice(pool)
        char_data = data_manager.find_item("characters", char_key)
        char_name = char_data["name"] if char_data else char_key.replace("_", " ").title()

        add_to_inventory(user_id, char_key, char_name, rarity)
        pulls.append((char_name, rarity))

    progress_daily_quest(user_id, "gacha")
    add_rewards(user_id, username, 80, 150)

    res_list = []
    for i, (name, rarity) in enumerate(pulls, 1):
        res_list.append(f"{i}. **[{rarity}]** {name}")

    res = (
        f"🎪 **GACHA 10X MULTI-SUMMON** 🎪\n\n"
        + "\n".join(res_list) + "\n\n"
        f"✨ All units saved to your inventory! Use `/inventory` to view your character vault! 👑"
    )
    await update.message.reply_text(res, parse_mode="Markdown")

async def inventory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    inv = get_inventory(user_id)
    if not inv:
        await update.message.reply_text("📪 **Your Character Vault is empty!**\n\nRun `/gacha` or `/gacha10` to summon powerful units!", parse_mode="Markdown")
        return

    inv_list = []
    for name, rarity, count in inv:
        stars = "⭐" if rarity in ["SP", "SSR"] else "▫️"
        inv_list.append(f"• **[{rarity}]** {name} x{count} {stars}")

    res = (
        f"🏛️ **GACHA CHARACTER VAULT FOR {username.upper()}** 🏛️\n\n"
        + "\n".join(inv_list) + "\n\n"
        f"💎 *Keep summoning to upgrade your collection level!*"
    )
    await update.message.reply_text(res, parse_mode="Markdown")

async def games_menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = (
        "🎮 **AKATSUKI CASINO & MINI-GAMES SUITE** 🎮\n\n"
        "Start lobbies for multiplayer games or play single player games!\n\n"
        "🎮 **AVAILABLE GAMES:**\n"
        "1. **Trivia** - Test your lore knowledge across categories!\n"
        "   - Syntax: `/play trivia` (Multiplayer)\n"
        "2. **Scramble** - Speed unscramble famous characters & terms!\n"
        "   - Syntax: `/play scramble`\n"
        "3. **Dice** - Classic dice-roll brawls with multipliers!\n"
        "   - Syntax: `/dice`\n"
        "4. **Blackjack** - Classic card table duel. Stand or Hit!\n"
        "   - Syntax: `/play blackjack`\n"
        "5. **Mines** - Grid minesweeper game with cash multiplier bets!\n"
        "   - Syntax: `/play mines`\n\n"
        "✨ *All games reward substantial XP, Coins, and prestige levels upon victory!* 🎉"
    )
    await update.message.reply_text(res, parse_mode="Markdown")

async def play_lobby_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: `/play <trivia|scramble|blackjack|mines>`", parse_mode="Markdown")
        return

    game_type = context.args[0].lower().strip()
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    if game_type not in ['trivia', 'scramble', 'blackjack', 'mines', 'hangman']:
        await update.message.reply_text("❌ Unknown game type. Use `/games` to see available games.")
        return

    mode = "multiplayer" if game_type in ["trivia", "scramble", "blackjack"] else "solo"
    msg = game_manager.start_lobby(chat_id, game_type, mode=mode)

    # Auto join the creator
    game_manager.join_lobby(chat_id, user_id, username)

    await update.message.reply_text(msg + f"\n\n👤 **Lobby Host:** {username} has automatically joined!", parse_mode="Markdown")

async def start_game_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    ok, start_msg = game_manager.start_game(chat_id)
    if ok:
        await update.message.reply_text(start_msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Failed to start game. Make sure a lobby is active and players have joined!")

async def reminder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    member = await context.bot.get_chat_member(chat_id, user_id)
    if member.status not in [ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
        await update.message.reply_text("❌ This command is restricted to administrators.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /reminder [on|off|status|15|30|60]")
        return

    sub = context.args[0].lower()
    enabled, lead = get_reminder_settings(chat_id)

    if sub == "on":
        set_reminder_enabled(chat_id, True)
        await update.message.reply_text("✅ Event reminders enabled.")
    elif sub == "off":
        set_reminder_enabled(chat_id, False)
        await update.message.reply_text("🚫 Event reminders disabled.")
    elif sub == "status":
        status_text = "ENABLED" if enabled else "DISABLED"
        await update.message.reply_text(f"📊 REMINDER STATUS\n\nReminders: {status_text}\nLead Time: {lead} minutes")
    elif sub in ["15", "30", "60"]:
        set_reminder_lead(chat_id, int(sub))
        await update.message.reply_text(f"⏰ Reminder lead time set to {sub} minutes.")
    else:
        await update.message.reply_text("❌ Invalid argument. Use on, off, status, or 15/30/60.")

def main():
    if not TOKEN:
        logging.error("BOT_TOKEN bulunamadı! Lütfen environment variable olarak tanımlayın.")
        return

    init_db()

    application = Application.builder().token(TOKEN).build()

    async def set_commands(app):
        from botfather_helper import COMMANDS
        from telegram import BotCommand
        bot_commands = [BotCommand(cmd, desc) for cmd, desc in COMMANDS.items()]
        # Add new RPG commands to BotFather Menu dynamically!
        additional_cmds = {
            "play": "Start a game lobby (Trivia, Scramble, Blackjack, Mines)",
            "join": "Join an open game lobby",
            "startgame": "Start the joined lobby!",
            "games": "View game catalog & rules",
            "daily": "Claim daily Coin & XP rewards!",
            "profile": "View level, rank, XP, and achievements",
            "compare": "Compare two characters side-by-side",
            "quest": "View your randomized Daily active Quest!",
            "claimquest": "Claim rewards for completed quests!",
            "gacha": "Summon a randomized Bleach character!",
            "gacha10": "Perform a premium 10x character pull!",
            "inventory": "View your collected character inventory!"
        }
        for cmd, desc in additional_cmds.items():
            if cmd not in COMMANDS:
                bot_commands.append(BotCommand(cmd, desc))
        await app.bot.set_my_commands(bot_commands)

    application.post_init = set_commands

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("rules", rules))
    application.add_handler(CommandHandler("leaders", leaders))
    application.add_handler(CommandHandler("banner", banner))
    application.add_handler(CommandHandler("nextbanner", next_banner))
    application.add_handler(CommandHandler("events", events))
    application.add_handler(CommandHandler("translate", translate))
    application.add_handler(CommandHandler("score", score))
    application.add_handler(CommandHandler("leaderboard", leaderboard))
    application.add_handler(CommandHandler("math", math_game))
    application.add_handler(CommandHandler("dice", dice_game))
    application.add_handler(CommandHandler("join", join_game))
    application.add_handler(CommandHandler("emoji", emoji_game))
    application.add_handler(CommandHandler("quiz", quiz_game))
    application.add_handler(CommandHandler("build", build_command))
    application.add_handler(CommandHandler("cardinfo", card_info_command))
    application.add_handler(CommandHandler("character", character_command))
    application.add_handler(CommandHandler("assist", assist_command))
    application.add_handler(CommandHandler("guard", guard_command))
    application.add_handler(CommandHandler("bonds", bonds_command))
    application.add_handler(CommandHandler("meta", meta_command))
    application.add_handler(CommandHandler("event", event_command))
    application.add_handler(CommandHandler("shop", shop_command))
    application.add_handler(CommandHandler("bannerhistory", banner_history_command))
    application.add_handler(CommandHandler("compare", compare_command))
    application.add_handler(CommandHandler("tierlist", tierlist_command))
    application.add_handler(CommandHandler("news", news_command))
    application.add_handler(CommandHandler("ask", ask_command))
    application.add_handler(CommandHandler("updatedb", update_db_command))
    application.add_handler(CommandHandler("reminder", reminder_command))

    # RPG / Multiplayer command handlers
    application.add_handler(CommandHandler("daily", daily_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("games", games_menu_command))
    application.add_handler(CommandHandler("play", play_lobby_command))
    application.add_handler(CommandHandler("startgame", start_game_command))

    # Daily active Quest commands
    application.add_handler(CommandHandler("quest", quest_command))
    application.add_handler(CommandHandler("claimquest", claim_quest_command))

    # Gacha summon simulator commands
    application.add_handler(CommandHandler("gacha", gacha_command))
    application.add_handler(CommandHandler("gacha10", gacha10_command))
    application.add_handler(CommandHandler("inventory", inventory_command))

    # Admin Panel overriding settings commands
    application.add_handler(CommandHandler("admin_setnews", admin_setnews_command))
    application.add_handler(CommandHandler("admin_setbanner", admin_setbanner_command))
    application.add_handler(CommandHandler("admin_setevent", admin_setevent_command))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Member tracking
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.CHAT_MEMBER))

    # Scheduler repeating every 60s
    job_queue = application.job_queue
    job_queue.run_repeating(check_events, interval=60, first=10)

    application.run_polling(allowed_updates=[Update.MESSAGE, Update.CHAT_MEMBER, Update.MY_CHAT_MEMBER])

if __name__ == "__main__":
    main()
