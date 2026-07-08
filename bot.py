import os
import asyncio
import logging
from datetime import datetime, timedelta
from deep_translator import GoogleTranslator
from banner_data import BANNERS, REFERENCE_DATE, REFERENCE_DAY
from database import init_db, update_score, get_user_score, get_leaderboard
from game_manager import game_manager
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
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

def main():
    if not TOKEN:
        logging.error("BOT_TOKEN bulunamadı! Lütfen environment variable olarak tanımlayın.")
        return

    # Initialize database
    init_db()

    # Bot uygulamasını başlatıyoruz
    application = Application.builder().token(TOKEN).build()

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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Botu çalıştırıyoruz (Render gibi platformlar için en ideali polling'dir)
    application.run_polling()

if __name__ == "__main__":
    main()
    
