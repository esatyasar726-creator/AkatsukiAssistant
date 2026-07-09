from utils.leaderboard import get_top
    get_current_day,
    get_banner,
    get_next_banner,
    get_previous_banner,
)


@bot.message_handler(commands=["banner"])
def banner(message):
    day = get_current_day()
    data = get_banner(day)

    if not data:
        bot.reply_to(message, f"📅 Day {day}\n\nNo active banner.")
        return

    bot.reply_to(
        message,
        f"📅 Day {day}\n\n🎴 {data['type']}\n{data['name']}"
    )


@bot.message_handler(commands=["nextbanner"])
def next_banner(message):
    day, data = get_next_banner()

    bot.reply_to(
        message,
        f"➡️ Next Banner\n\n📅 Day {day}\n🎴 {data['type']}\n{data['name']}"
    )


@bot.message_handler(commands=["pastbanner"])
def past_banner(message):
    day, data = get_previous_banner()

    bot.reply_to(
        message,
        f"⬅️ Previous Banner\n\n📅 Day {day}\n🎴 {data['type']}\n{data['name']}"
    )


@bot.message_handler(commands=["help"])
def help_command(message):
    bot.reply_to(
        message,
        """🤖 AKATSUKI ASSISTANT

Available Commands

/start
/help
/rules
/leader
/banner
/nextbanner
/pastbanner
/events
/translate
/dailyquestion
/leaderboard"""
    )


@bot.message_handler(commands=["leader"])
def leader(message):
    bot.reply_to(
        message,
        """👑 AKATSUKI CLAN STAFF

👑 Leader
• Klaus

⚔ Vice Leaders
• Asta
• YurtSever

🛡 Admins
• Baba Yaga
• Jaco Tenma
• Mutoh"""
    )


@bot.message_handler(commands=["events"])
def events(message):
    bot.reply_to(
        message,
        """📅 CLAN EVENTS SCHEDULE

⚔ Clan War
Saturday 10:00 AM (Istanbul GMT+3)
Saturday 07:00 AM (GMT)

🔮 Inner

Istanbul
12:30 PM - 01:00 PM
08:30 PM - 09:00 PM

GMT
09:30 AM - 10:00 AM
05:30 PM - 06:00 PM

🏆 Top Vs

Istanbul
12:00 PM - 02:00 PM
08:00 PM - 10:00 PM

GMT
09:00 AM - 11:00 AM
05:00 PM - 07:00 PM

🏰 Las Noches

Istanbul
02:00 PM
04:00 PM
06:00 PM
10:00 PM
11:00 PM

GMT
11:00 AM
01:00 PM
03:00 PM
07:00 PM
08:00 PM"""
    )


@bot.message_handler(commands=["leaderboard"])
def leaderboard(message):
    ranking = get_top()

    if not ranking:
        bot.reply_to(message, "🏆 Leaderboard is empty.")
        return

    medals = ["🥇", "🥈", "🥉"]
    text = "🏆 AKATSUKI LEADERBOARD\n\n"

    for i, player in enumerate(ranking):
        medal = medals[i] if i < 3 else f"{i+1}."
        text += f"{medal} {player['username']} • {player['score']} pts\n"

    bot.reply_to(message, text)
