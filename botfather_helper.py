COMMANDS = {
    "start": "Welcome to Akatsuki Assistant",
    "help": "Show available commands",
    "rules": "Clan rules",
    "leaders": "Clan staff info",
    "banner": "Current character banner",
    "nextbanner": "Upcoming banner prediction",
    "events": "Weekly event schedule",
    "translate": "Translate a message (reply-only)",
    "score": "Check your game score",
    "leaderboard": "Top 10 players",
    "math": "Start math mini-game",
    "dice": "Start dice mini-game",
    "join": "Join active dice game",
    "emoji": "Start emoji guess game",
    "quiz": "Start trivia quiz",
    "cardinfo": "Expert card analysis",
    "character": "Detailed character info",
    "assist": "Assist character analysis",
    "guard": "Guard character analysis",
    "bonds": "View character bonds",
    "meta": "Current PvP/PvE meta",
    "event": "Events and rotations",
    "shop": "Shop value analysis",
    "bannerhistory": "Past banner release history",
    "compare": "Compare two characters/cards",
    "tierlist": "Character tier list",
    "news": "Latest game news",
    "ask": "Ask AI about the game"
}

def generate_botfather_list():
    print("Copy and paste this list to BotFather -> /setcommands:")
    print("-" * 20)
    for cmd, desc in COMMANDS.items():
        print(f"{cmd} - {desc}")
    print("-" * 20)

if __name__ == "__main__":
    generate_botfather_list()
