import os
import logging

from database import (
    init_db,
    update_user_stats,
    get_user_profile
)

from game_manager import game_manager
from formatters import format_profile

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
🤖 AKATSUKI ULTIMATE BOT

Komutlar:

/start - Botu başlatır
/help - Yardım menüsü
/profile - Profil bilgisi

Oyunlar:

/trivia - Bilgi yarışması
/math - Matematik oyunu
/emoji - Emoji tahmini
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚔ Akatsuki Ultimate Bot aktif!\n\n/help yazarak komutlara bakabilirsin."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP)


async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    data = get_user_profile(user_id)

    if data:
        await update.message.reply_text(
            format_profile(data)
        )
    else:
        await update.message.reply_text(
            "Henüz profilin yok. Oyun oynayarak başlayabilirsin."
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


    games = [
        ("trivia",20),
        ("math",10),
        ("emoji",15)
    ]


    for game,reward in games:

        key = f"{game}_{chat_id}"

        if key in context.bot_data:

            if text == str(context.bot_data[key]).lower():

                update_user_stats(
                    user.id,
                    user.username or user.first_name,
                    coins=reward,
                    xp=reward*2
                )


                del context.bot_data[key]


                await update.message.reply_text(
                    f"✅ Doğru cevap!\n{reward} coin ve {reward*2} XP kazandın."
                )

                return



async def main():

    if not TOKEN:
        logging.error("BOT_TOKEN bulunamadı!")
        return


    init_db()


    async def post_init(application):

        commands = [

            BotCommand("help","Yardım"),
            BotCommand("profile","Profil"),
            BotCommand("trivia","Bilgi oyunu"),
            BotCommand("math","Matematik"),
            BotCommand("emoji","Emoji oyunu")

        ]

        await application.bot.set_my_commands(commands)



    app = (
        Application
        .builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )


    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("help",help_command))
    app.add_handler(CommandHandler("profile",profile_command))

    app.add_handler(CommandHandler("trivia",trivia_command))
    app.add_handler(CommandHandler("math",math_command))
    app.add_handler(CommandHandler("emoji",emoji_command))


    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )


    app.run_polling()



if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
