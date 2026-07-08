import os
import logging
from banner_data import BANNERS
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
/bannerlist
/events
/next
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚔ Welcome to Akatsuki Assistant!\n\nUse /help to see all commands."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP)


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(RULES)


async def leaders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(LEADERS)
