import logging
import os
from datetime import datetime, time
import pytz
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv
from deep_translator import GoogleTranslator

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define timezone for Turkey
TR_TZ = pytz.timezone("Europe/Istanbul")

# Define event schedule
EVENTS = [
    {"name": "Gelişmiş Gemi", "time": time(0, 0)},
    {"name": "Efsanevi Canavar", "time": time(10, 0)},
    {"name": "Klan Akını", "time": time(11, 0)},
    {"name": "Dünya Patronu", "time": time(12, 30)},
    {"name": "Korsan Gemisi", "time": time(16, 0)},
    {"name": "Efsanevi Canavar", "time": time(17, 0)},
    {"name": "Klan Akını", "time": time(19, 0)},
    {"name": "Dünya Patronu", "time": time(20, 0)},
    {"name": "Korsan Gemisi", "time": time(21, 30)},
]

# Initialize translator
translator = GoogleTranslator(source="auto", target="tr")

# Define commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Selam {user.mention_html()}! Ben Akatsuki Yardımcısıyım. "
        "Botun tüm özelliklerini görmek için /help yazabilirsin."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "🤖 **Akatsuki Yardımcısı Komut Listesi** 🤖\n\n"
        "/start - Botu başlatır ve selamlama mesajı gönderir.\n"
        "/help - Bu yardım mesajını gösterir.\n"
        "/etkinlik - Günlük oyun içi etkinliklerin saatlerini listeler.\n"
        "/cevir <metin> - Yazdığınız metni otomatik olarak Türkçe'ye çevirir.\n"
        "/zar - 1 ile 6 arasında rastgele bir sayı döndürür.\n"
        "/yazitura - Rastgele 'Yazı' veya 'Tura' sonucu verir.\n"
        "/sayitahmin <sayı> - 1 ile 10 arasında bir sayı tahmin etme oyunu."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def etkinlik(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List event schedule and show time remaining for the next event."""
    now_tr = datetime.now(TR_TZ)
    current_time = now_tr.time()
    current_date = now_tr.date()
    
    response = "📅 **Akatsuki Etkinlik Saatleri (TSİ)** 📅\n"
    response += "--------------------------------------\n"
    
    next_event = None
    min_diff = None
    
    for event in EVENTS:
        event_time_str = event["time"].strftime("%H:%M")
        response += f"• {event['name']}: {event_time_str}\n"
        
        event_datetime = datetime.combine(current_date, event["time"])
        event_datetime = TR_TZ.localize(event_datetime)
        
        if event["time"] > current_time:
            diff = event_datetime - now_tr
        else:
            # If the event is tomorrow
            from datetime import timedelta
            tomorrow = current_date + timedelta(days=1)
            event_datetime_tomorrow = datetime.combine(tomorrow, event["time"])
            event_datetime_tomorrow = TR_TZ.localize(event_datetime_tomorrow)
            diff = event_datetime_tomorrow - now_tr
            
        if min_diff is None or diff < min_diff:
            min_diff = diff
            next_event = event
            
    response += "--------------------------------------\n"
    if next_event:
        hours, remainder = divmod(int(min_diff.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        
        time_rem_str = ""
        if hours > 0:
            time_rem_str += f"{hours} saat "
        time_rem_str += f"{minutes} dakika"
        
        response += f"⏳ **Sıradaki Etkinlik:** {next_event['name']} ({next_event['time'].strftime('%H:%M')})\n"
        response += f"⏱ **Kalan Süre:** {time_rem_str}"
        
    await update.message.reply_text(response, parse_mode="Markdown")

async def cevir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Translate text to Turkish."""
    if not context.args:
        await update.message.reply_text(
            "Lütfen çevirmek istediğiniz metni komuttan sonra yazın.\n"
            "Örnek: `/cevir hello world`",
            parse_mode="Markdown"
        )
        return
        
    text_to_translate = " ".join(context.args)
    try:
        translated_text = translator.translate(text_to_translate)
        await update.message.reply_text(
            f"🔤 **Orijinal:** {text_to_translate}\n"
            f"🇹🇷 **Türkçe Çeviri:** {translated_text}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await update.message.reply_text("Çeviri yapılırken bir hata oluştu.")

import random

async def zar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Roll a dice (1-6)."""
    result = random.randint(1, 6)
    await update.message.reply_text(f"🎲 Zar attın: **{result}**", parse_mode="Markdown")

async def yazitura(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Flip a coin (Yazı/Tura)."""
    result = random.choice(["Yazı", "Tura"])
    await update.message.reply_text(f"🪙 Parayı havaya attın... Sonuç: **{result}**!", parse_mode="Markdown")

async def sayitahmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """A simple number guessing game (1-10)."""
    if not context.args:
        await update.message.reply_text(
            "Lütfen 1 ile 10 arasında bir tahmin girin.\n"
            "Örnek: `/sayitahmin 5`",
            parse_mode="Markdown"
        )
        return
        
    try:
        user_guess = int(context.args[0])
        if user_guess < 1 or user_guess > 10:
            await update.message.reply_text("Lütfen sadece 1 ile 10 arasında bir sayı girin.")
            return
            
        secret_number = random.randint(1, 10)
        if user_guess == secret_number:
            await update.message.reply_text(f"🎉 Tebrikler! Doğru tahmin ettin, sayı **{secret_number}** idi!", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"❌ Maalesef yanlış tahmin. Doğru sayı **{secret_number}** idi. Tekrar dene!", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("Lütfen geçerli bir sayı girin.")

def main() -> None:
    """Start the bot."""
    if not TOKEN:
        logger.error("BOT_TOKEN format error or not found in environment variables.")
        return

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("etkinlik", etkinlik))
    application.add_handler(CommandHandler("cevir", cevir))
    application.add_handler(CommandHandler("zar", zar))
    application.add_handler(CommandHandler("yazitura", yazitura))
    application.add_handler(CommandHandler("sayitahmin", sayitahmin))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
    
