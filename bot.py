import os
import logging
import random

from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

logging.basicConfig(
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")


users = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    users[user.id] = {
        "name": user.first_name,
        "xp": 0,
        "coin": 0
    }

    await update.message.reply_text(
        f"⚔ Hoş geldin {user.first_name}!\n\n/help yazarak komutları görebilirsin."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        """
🤖 AKATSUKI BOT

Komutlar:

/start - Başlat
/profile - Profil
/math - Matematik oyunu
/trivia - Bilgi sorusu
"""
    )


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if user.id not in users:
        users[user.id] = {
            "name": user.first_name,
            "xp": 0,
            "coin": 0
        }

    data = users[user.id]

    await update.message.reply_text(
        f"""
👤 Profil

İsim: {data['name']}
⭐ XP: {data['xp']}
💰 Coin: {data['coin']}
"""
    )


async def math_game(update: Update, context: ContextTypes.DEFAULT_TYPE):

    a = random.randint(1,20)
    b = random.randint(1,20)

    answer = a + b

    context.chat_data["math_answer"] = answer

    await update.message.reply_text(
        f"🧮 {a} + {b} = ?"
    )


async def trivia(update: Update, context: ContextTypes.DEFAULT_TYPE):

    questions = [
        ("Türkiye'nin başkenti?", "ankara"),
        ("Bleach ana karakteri?", "ichigo"),
        ("2+2 kaç?", "4")
    ]

    q,a = random.choice(questions)

    context.chat_data["trivia_answer"] = a

    await update.message.reply_text(
        f"📚 {q}"
    )


async def answer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text.lower().strip()

    answer = None

    if "math_answer" in context.chat_data:
        answer = str(context.chat_data["math_answer"])

    if "trivia_answer" in context.chat_data:
        answer = context.chat_data["trivia_answer"]


    if answer and text == answer:

        user = update.effective_user

        if user.id not in users:
            users[user.id] = {
                "name": user.first_name,
                "xp": 0,
                "coin": 0
            }

        users[user.id]["xp"] += 10
        users[user.id]["coin"] += 5


        await update.message.reply_text(
            "✅ Doğru cevap!\n+10 XP\n+5 Coin"
        )

        context.chat_data.clear()



async def post_init(app):

    await app.bot.set_my_commands(
        [
            BotCommand("start","Başlat"),
            BotCommand("help","Yardım"),
            BotCommand("profile","Profil"),
            BotCommand("math","Matematik"),
            BotCommand("trivia","Bilgi")
        ]
    )



def main():

    if not TOKEN:
        print("BOT_TOKEN yok!")
        return


    app = (
        Application
        .builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )


    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("profile", profile))

    app.add_handler(CommandHandler("math", math_game))
    app.add_handler(CommandHandler("trivia", trivia))


    from telegram.ext import MessageHandler, filters

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            answer_handler
        )
    )


    app.run
