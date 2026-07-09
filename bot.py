import os
import logging
import asyncio

from database import (
    init_db,
    update_user_stats,
    get_user_profile
)

from game_manager import game_manager

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


TOKEN = os.getenv("BOT_TOKEN")


HELP = """
🤖 AKATSUKI BOT

Komutlar:

/start - Botu başlatır
/help - Yardım
/profile - Profil

Oyunlar:

/trivia - Bilgi yarışması
/math - Matematik oyunu
/emoji - Emoji tahmini
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚔ Akatsuki Bot aktif!\n\n/help yazarak komutları görebilirsin."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP)


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    data = get_user_profile(
        update.effective_user.id
    )

    if data:
        await update.message.reply_text(
            f"👤 Profil:\n\n{data}"
        )
    else:
        await update.message.reply_text(
            "Henüz profil bulunamadı."
        )


async def trivia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q, a = game_manager.start_trivia()

    context.bot_data[f"trivia_{update.effective_chat.id}"] = a

    await update.message.reply_text(
        f"📚 TRIVIA\n\n{q}"
    )


async def math_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q, a = game_manager.start_math_challenge()

    context.bot_data[f"math_{update.effective_chat.id}"] = a

    await update.message.reply_text(
        f"🧮 MATH\n\n{q}"
    )


async def emoji_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    e, a = game_manager.start_emoji_guess()

    context.bot_data[f"emoji_{update.effective_chat.id}"] = a

    await update.message.reply_text(
        f"🧩 EMOJI\n\n{e}"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message or not update.message.text:
        return

    text = update.message.text.lower().strip()
    user = update.effective_user
    chat_id = update.effective_chat.id


    for game, reward in [
        ("trivia",20),
        ("math",10),
        ("emoji",
