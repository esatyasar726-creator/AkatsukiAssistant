import os
import asyncio
import logging
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
from banner_data import BANNERS, REFERENCE_DATE, REFERENCE_DAY
from database import (
    init_db, update_score, get_user_score, get_leaderboard,
    add_chat_member, remove_chat_member, get_chat_members,
    set_reminder_enabled, set_reminder_lead, get_reminder_settings,
    get_all_chats_with_reminders
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
🤖 Akatsuki Assistant

Available Commands

/start
/help
/rules
/leaders
/banner
/nextbanner
/events
/translate
/score
/leaderboard
/math
/dice
/join
/emoji
/quiz
/build <character>
/cardinfo <card>
/character <name>
/assist <name>
/guard <name>
/bonds <character>
/meta
/event
/shop
/banner
/compare <c1> vs <c2>
/tierlist
/news
/ask <question>
/reminder [on|off|status|15|30|60]
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚔ Welcome to Akatsuki Assistant!\n\nUse /help to see all commands.")

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

    # Find the active banner (highest day <= current day)
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
    pts = get_user_score(user_id)
    await update.message.reply_text(f"👤 {username}, your total score is: {pts} points.")

async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_users = get_leaderboard()
    if not top_users:
        await update.message.reply_text("The leaderboard is currently empty.")
        return

    text = "🏆 AKATSUKI TOP 10 LEADERBOARD\n\n"
    for i, (username, pts) in enumerate(top_users, 1):
        text += f"{i}. {username or 'Unknown'}: {pts} pts\n"
    await update.message.reply_text(text)

async def math_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question, answer = game_manager.start_math_challenge()
    chat_id = update.effective_chat.id

    # Store answer in context for checking
    if 'math_answers' not in context.bot_data:
        context.bot_data['math_answers'] = {}
    context.bot_data['math_answers'][chat_id] = answer

    await update.message.reply_text(f"🧮 MATH CHALLENGE!\nFirst one to answer gets 10 points!\n\n{question}")

async def track_chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tracks the members in the chat."""
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
        logging.info(f"User {username} joined chat {chat_id}")
    elif was_member and not is_member:
        remove_chat_member(chat_id, user_id)
        logging.info(f"User {username} left chat {chat_id}")

EVENT_SCHEDULE = [
    # (Day 0=Mon, Hour, Minute, Name) - Using Istanbul GMT+3 times as base
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
    # Current time in GMT+3 (Istanbul)
    now = datetime.utcnow() + timedelta(hours=3)
    current_day = now.weekday()

    chats = get_all_chats_with_reminders()
    for chat_id, lead_minutes in chats:
        for event_day, event_hour, event_minute, event_name in EVENT_SCHEDULE:
            event_time = now.replace(hour=event_hour, minute=event_minute, second=0, microsecond=0)

            # Adjust day if schedule is for another day
            if event_day != current_day:
                continue

            reminder_time = event_time - timedelta(minutes=lead_minutes)

            # Check if now is within the minute of reminder_time
            if now.hour == reminder_time.hour and now.minute == reminder_time.minute:
                members = get_chat_members(chat_id)
                if not members:
                    continue

                mentions = [f"@{m[1]}" for m in members if m[1]]

                # Split mentions into chunks (e.g., 50 per message is safe for most groups)
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
    chat_id = update.effective_chat.id
    text = update.message.text.lower().strip()

    # Check for math game answer
    if 'math_answers' in context.bot_data and chat_id in context.bot_data['math_answers']:
        correct_answer = context.bot_data['math_answers'][chat_id]
        try:
            if int(text) == correct_answer:
                user_id = update.effective_user.id
                username = update.effective_user.username or update.effective_user.first_name
                new_score = update_score(user_id, username, 10)
                del context.bot_data['math_answers'][chat_id]
                await update.message.reply_text(f"✅ Correct! {username} earned 10 points! Total: {new_score}")
                return
        except ValueError:
            pass

    # Check for emoji game answer
    if 'emoji_answers' in context.bot_data and chat_id in context.bot_data['emoji_answers']:
        correct_answer = context.bot_data['emoji_answers'][chat_id]
        if text == correct_answer:
            user_id = update.effective_user.id
            username = update.effective_user.username or update.effective_user.first_name
            new_score = update_score(user_id, username, 15)
            del context.bot_data['emoji_answers'][chat_id]
            await update.message.reply_text(f"✅ Correct! It was {correct_answer}! {username} earned 15 points! Total: {new_score}")
            return

    # Check for quiz answer
    if 'quiz_answers' in context.bot_data and chat_id in context.bot_data['quiz_answers']:
        correct_answer = context.bot_data['quiz_answers'][chat_id]
        if text == correct_answer:
            user_id = update.effective_user.id
            username = update.effective_user.username or update.effective_user.first_name
            new_score = update_score(user_id, username, 20)
            del context.bot_data['quiz_answers'][chat_id]
            await update.message.reply_text(f"✅ Correct! The answer was {correct_answer.capitalize()}! {username} earned 20 points! Total: {new_score}")
            return

async def dice_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    msg = game_manager.start_dice_game(chat_id)
    await update.message.reply_text(msg)

    # Start timer to resolve game
    await asyncio.sleep(30)

    result = game_manager.resolve_dice_game(chat_id)
    if not result:
        return

    if isinstance(result, str):
        await context.bot.send_message(chat_id=chat_id, text=result)
        return

    results, winner_id, winner_name = result
    new_score = update_score(winner_id, winner_name, 20)

    res_text = "🎲 DICE GAME RESULTS:\n" + "\n".join(results)
    res_text += f"\n\n🏆 Winner: {winner_name} (+20 points)! Total: {new_score}"
    await context.bot.send_message(chat_id=chat_id, text=res_text)

async def join_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    username = update.effective_user.username or update.effective_user.first_name

    if game_manager.join_dice_game(chat_id, user_id, username):
        await update.message.reply_text(f"✅ {username} joined the dice game!")
    else:
        await update.message.reply_text("❌ No game to join or you are already in.")

async def emoji_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emoji, answer = game_manager.start_emoji_guess()
    chat_id = update.effective_chat.id

    if 'emoji_answers' not in context.bot_data:
        context.bot_data['emoji_answers'] = {}
    context.bot_data['emoji_answers'][chat_id] = answer

    await update.message.reply_text(f"🧩 EMOJI GUESS!\nWhat does this emoji represent? (15 points)\n\n{emoji}")

async def quiz_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question, answer = game_manager.start_quiz()
    chat_id = update.effective_chat.id

    if 'quiz_answers' not in context.bot_data:
        context.bot_data['quiz_answers'] = {}
    context.bot_data['quiz_answers'][chat_id] = answer

    await update.message.reply_text(f"📖 QUIZ TIME!\nFirst to answer correctly gets 20 points!\n\n{question}")

async def build_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /build <character name>")
        return
    char_name = " ".join(context.args)
    char_data = data_manager.find_item("characters", char_name)
    if char_data:
        response = format_character_info(char_data) # Builds use char data
    else:
        response = get_build_response(char_name)
    await update.message.reply_text(response, parse_mode="Markdown")

async def card_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /cardinfo <card name>")
        return
    query = " ".join(context.args)
    card_data = data_manager.find_item("cards", query)
    if card_data:
        response = format_card_info(card_data)
    else:
        response = get_card_analysis(query)
    await update.message.reply_text(response, parse_mode="Markdown")

async def update_db_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Restrict to admins if possible, but for now simple update
    await update.message.reply_text("🔄 Updating database from external sources... Please wait.")
    from data_updater import update_database
    update_database()
    data_manager.reload()
    await update.message.reply_text("✅ Database successfully updated!")

async def character_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /character <character name>")
        return
    query = " ".join(context.args)
    char_data = data_manager.find_item("characters", query)
    response = format_character_info(char_data)
    await update.message.reply_text(response, parse_mode="Markdown")

async def assist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assist character data coming soon! Try /character for now.")

async def guard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Guard character data coming soon! Try /character for now.")

async def bonds_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /bonds <character name>")
        return
    query = " ".join(context.args)
    char_data = data_manager.find_item("characters", query)
    if char_data:
        b = char_data['bonds']
        res = f"🔗 **Bonds for {char_data['name']}:**\n\n"
        res += f"⚔️ ATK: {', '.join(b['attack'])}\n"
        res += f"❤️ HP: {', '.join(b['hp'])}\n"
        res += f"🛡️ DEF: {', '.join(b['defense'])}"
        await update.message.reply_text(res, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Character not found.")

async def meta_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    meta_data = data_manager.get_meta()
    response = format_meta(meta_data)
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
    await update.message.reply_text("🛒 Shop rotations and value analysis coming soon!")

async def banner_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📜 Full Banner history analysis coming soon!")

async def compare_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🆚 Comparison tool coming soon! Use /cardinfo or /character for individual stats.")

async def tierlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await meta_command(update, context)

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await event_command(update, context)

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /ask <your question about Bleach Mobile 3D>")
        return
    query = " ".join(context.args)
    response = get_ai_response(query)
    await update.message.reply_text(response, parse_mode="Markdown")

async def reminder_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    # Administrator check
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

    # Initialize database
    init_db()

    # Bot uygulamasını başlatıyoruz
    application = Application.builder().token(TOKEN).build()

    # Register commands with Telegram for the "/" menu
    async def set_commands(app):
        from botfather_helper import COMMANDS
        from telegram import BotCommand
        bot_commands = [BotCommand(cmd, desc) for cmd, desc in COMMANDS.items()]
        await app.bot.set_my_commands(bot_commands)

    # Note: application.post_init can be used to run set_commands
    application.post_init = set_commands

    # Komutları kaydediyoruz
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
    application.add_handler(CommandHandler("banner", banner_history_command))
    application.add_handler(CommandHandler("compare", compare_command))
    application.add_handler(CommandHandler("tierlist", tierlist_command))
    application.add_handler(CommandHandler("news", news_command))
    application.add_handler(CommandHandler("ask", ask_command))
    application.add_handler(CommandHandler("updatedb", update_db_command))
    application.add_handler(CommandHandler("reminder", reminder_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Member tracking
    application.add_handler(ChatMemberHandler(track_chats, ChatMemberHandler.CHAT_MEMBER))

    # Scheduler
    job_queue = application.job_queue
    job_queue.run_repeating(check_events, interval=60, first=10)

    # Botu çalıştırıyoruz (Render gibi platformlar için en ideali polling'dir)
    application.run_polling(allowed_updates=[Update.MESSAGE, Update.CHAT_MEMBER, Update.MY_CHAT_MEMBER])

if __name__ == "__main__":
    main()
    
