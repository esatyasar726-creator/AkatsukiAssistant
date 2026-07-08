import os
import logging
from datetime import datetime, timedelta
from banner_data import BANNERS, REFERENCE_DATE, REFERENCE_DAY
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
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

🥈 Vice Leader
Asta

🛡 Admin
YurtSever
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
        "Saturday 10:00 (Istanbul GMT+3)\n"
        "Saturday 07:00 (GMT)\n\n"
        "🔮 Inner\n"
        "12:30-13:00, 20:30-21:00 (Istanbul GMT+3)\n"
        "09:30-10:00, 17:30-18:00 (GMT)\n\n"
        "🏆 Top Vs\n"
        "12:00-14:00, 20:00-22:00 (Istanbul GMT+3)\n"
        "09:00-11:00, 17:00-19:00 (GMT)\n\n"
        "🏰 Las Noches\n"
        "14:00, 16:00, 18:00, 22:00, 23:00 (Istanbul GMT+3)\n"
        "11:00, 13:00, 15:00, 19:00, 20:00 (GMT)"
    )
    await update.message.reply_text(events_text)

def main():
    if not TOKEN:
        logging.error("BOT_TOKEN bulunamadı! Lütfen environment variable olarak tanımlayın.")
        return

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

    # Botu çalıştırıyoruz (Render gibi platformlar için en ideali polling'dir)
    application.run_polling()

if __name__ == "__main__":
    main()
    
