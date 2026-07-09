import random
import game_data

class GameManager:
    def __init__(self):
        # chat_id -> game_lobby dict
        self.active_games = {}

    # --- Backwards compatibility methods ---
    def start_math_challenge(self):
        # Legacy math game
        q, a = game_data.generate_math_question()
        return q, int(a) if a.isdigit() else a

    def start_emoji_guess(self):
        # Legacy emoji game
        emojis = {
            "🍎": "apple", "🍌": "banana", "🚗": "car", "🏠": "house",
            "🐱": "cat", "🐶": "dog", "⚽": "football", "🍕": "pizza"
        }
        emoji = random.choice(list(emojis.keys()))
        return emoji, emojis[emoji]

    def start_quiz(self):
        # Legacy quiz game
        return game_data.get_random_question("Bleach")

    def start_dice_game(self, chat_id):
        # Legacy dice game
        self.active_games[chat_id] = {
            'type': 'dice',
            'players': {}, # user_id -> {name, roll}
            'status': 'joining',
            'mode': 'multiplayer',
            'max_players': 5
        }
        return "🎲 Dice Game Lobby Opened! Use /join to participate. (Wait 30s for the game to start)"

    def join_dice_game(self, chat_id, user_id, username):
        lobby = self.active_games.get(chat_id)
        if lobby and lobby['type'] == 'dice' and lobby['status'] == 'joining':
            if user_id not in lobby['players']:
                lobby['players'][user_id] = {'name': username, 'roll': None}
                return True
        return False

    def resolve_dice_game(self, chat_id):
        lobby = self.active_games.get(chat_id)
        if not lobby or lobby['type'] != 'dice':
            return None

        players = lobby['players']
        if not players:
            if chat_id in self.active_games:
                del self.active_games[chat_id]
            return "No players joined."

        results = []
        for uid in players:
            roll = random.randint(1, 6)
            players[uid]['roll'] = roll
            results.append(f"{players[uid]['name']}: {roll}")

        # Determine winner
        max_roll = max(p['roll'] for p in players.values())
        winners = [uid for uid, p in players.items() if p['roll'] == max_roll]

        winner_id = winners[0]
        winner_name = players[winner_id]['name']

        if chat_id in self.active_games:
            del self.active_games[chat_id]
        return results, winner_id, winner_name

    # --- Advanced Lobby and Multiplayer / Tournament Game Suite ---
    def start_lobby(self, chat_id, game_type, mode="solo", max_players=5):
        # Standardize modern games
        self.active_games[chat_id] = {
            'type': game_type,
            'players': {}, # user_id -> {'name': name, 'score': 0, 'bet': 0, 'state': 'active'}
            'status': 'joining',
            'mode': mode,
            'max_players': max_players,
            'extra': {}, # game-specific states
            'questions': [] # for quiz/trivia tournaments
        }

        # Prepopulate game assets
        if game_type in ['trivia', 'quiz_battle', 'survival_quiz']:
            # Pull 5 questions for tournaments / rounds
            category = "General Knowledge"
            if game_type == 'quiz_battle':
                category = random.choice(list(game_data.TRIVIA_QUESTIONS.keys()))
            for _ in range(5):
                q, a = game_data.get_random_question(category)
                self.active_games[chat_id]['questions'].append((q, a))
        elif game_type == 'hangman':
            words = ["shinigami", "bankai", "hollow", "quincy", "espada", "soul society", "hogyoku", "zanpakuto"]
            word = random.choice(words)
            self.active_games[chat_id]['extra']['word'] = word
            self.active_games[chat_id]['extra']['guesses'] = []
            self.active_games[chat_id]['extra']['lives'] = 6
        elif game_type == 'mines':
            grid = [0] * 25 # 0 for safe, 1 for mine
            mine_indices = random.sample(range(25), 5) # 5 mines
            for idx in mine_indices:
                grid[idx] = 1
            self.active_games[chat_id]['extra']['grid'] = grid
            self.active_games[chat_id]['extra']['opened'] = []
        elif game_type == 'scramble':
            words = ["aizen", "ichigo", "byakuya", "yamamoto", "rukia", "orihime", "grimjow", "ulquiorra"]
            word = random.choice(words)
            scrambled = "".join(random.sample(word, len(word)))
            self.active_games[chat_id]['extra']['word'] = word
            self.active_games[chat_id]['extra']['scrambled'] = scrambled

        return f"🎮 **Lobby Opened:** `{game_type.upper()}` ({mode.upper()} mode, up to {max_players} players)\nUse `/join` to join the lobby!"

    def join_lobby(self, chat_id, user_id, username, bet=0):
        lobby = self.active_games.get(chat_id)
        if not lobby or lobby['status'] != 'joining':
            return False, "❌ There is no active lobby in joining status in this chat."

        if len(lobby['players']) >= lobby['max_players']:
            return False, "❌ The game lobby is already full!"

        if user_id in lobby['players']:
            return False, "⚠️ You are already in the lobby!"

        lobby['players'][user_id] = {
            'name': username,
            'score': 0,
            'bet': bet,
            'state': 'active'
        }
        return True, f"✅ **{username}** joined the lobby! ({len(lobby['players'])}/{lobby['max_players']} players)"

    def start_game(self, chat_id):
        lobby = self.active_games.get(chat_id)
        if not lobby or lobby['status'] != 'joining':
            return False, "❌ No lobby to start."

        if not lobby['players']:
            return False, "❌ Cannot start a game with 0 players!"

        lobby['status'] = 'playing'

        # Format the start message based on game type
        gt = lobby['type']
        if gt in ['trivia', 'quiz_battle', 'survival_quiz']:
            q, a = lobby['questions'][0]
            lobby['extra']['current_round'] = 0
            lobby['extra']['answer'] = a
            return True, f"📖 **Round 1:** First to answer correctly gets rewards!\n\n**Question:** {q}"
        elif gt == 'hangman':
            word = lobby['extra']['word']
            masked = " ".join(["_" if c != " " else "  " for c in word])
            return True, f"🪓 **Hangman Started!** Guess the word letter-by-letter using `/guess <letter>`.\n\n`{masked}`\nLives remaining: ❤️ 6"
        elif gt == 'mines':
            return True, f"💣 **Mines Started!** A 5x5 grid has 5 hidden mines. Reveal safe spots using `/mines_reveal <1-25>` to multiply your cash!"
        elif gt == 'scramble':
            scrambled = lobby['extra']['scrambled']
            return True, f"🧩 **Word Scramble!** Unscramble this name:\n\n`{scrambled}`\n\nSubmit your answer directly by typing it!"
        elif gt == 'blackjack':
            # Deal initial cards to players
            deck = [2,3,4,5,6,7,8,9,10,10,10,10,11] * 4
            random.shuffle(deck)
            lobby['extra']['deck'] = deck

            dealer = [random.choice(deck), random.choice(deck)]
            lobby['extra']['dealer'] = dealer

            for pid, p in lobby['players'].items():
                p_hand = [random.choice(deck), random.choice(deck)]
                p['hand'] = p_hand
                p['stand'] = False

            p_list = []
            for p in lobby['players'].values():
                p_list.append(f"• **{p['name']}**: {p['hand']} (Total: {sum(p['hand'])})")

            return True, (
                f"🃏 **Blackjack Started!**\n\n"
                f"**Dealer's Hand:** [{dealer[0]}, ?]\n"
                f"**Players:**\n" + "\n".join(p_list) + "\n\n"
                f"Use `/hit` to take a card, or `/stand` to hold."
            )

        return True, f"🎮 Game '{gt}' started!"

    def handle_lobby_answer(self, chat_id, user_id, text):
        lobby = self.active_games.get(chat_id)
        if not lobby or lobby['status'] != 'playing':
            return None

        gt = lobby['type']
        if gt in ['trivia', 'quiz_battle', 'survival_quiz']:
            ans = lobby['extra']['answer'].lower().strip()
            if text.lower().strip() == ans:
                # User guessed correctly
                p = lobby['players'].get(user_id)
                p_name = p['name'] if p else "Player"

                # Setup rewards
                xp = 25
                coins = 50

                # Check if tournament mode
                round_idx = lobby['extra'].get('current_round', 0)
                if round_idx + 1 < len(lobby['questions']):
                    # Next round
                    lobby['extra']['current_round'] += 1
                    next_q, next_a = lobby['questions'][lobby['extra']['current_round']]
                    lobby['extra']['answer'] = next_a
                    return {
                        'correct': True,
                        'resolved': False,
                        'winner_name': p_name,
                        'winner_id': user_id,
                        'coins': coins,
                        'xp': xp,
                        'msg': f"✅ **{p_name}** got it correct! (Answer was: {ans.capitalize()})\n\n📖 **Round {lobby['extra']['current_round'] + 1}:**\n**Question:** {next_q}"
                    }
                else:
                    # Resolve game
                    del self.active_games[chat_id]
                    return {
                        'correct': True,
                        'resolved': True,
                        'winner_name': p_name,
                        'winner_id': user_id,
                        'coins': coins,
                        'xp': xp,
                        'msg': f"🏆 **Game Over!** **{p_name}** answered the final question correctly! (Answer: {ans.capitalize()})\n\nYou have earned **{coins} Coins** and **{xp} XP**! 🎉"
                    }
        elif gt == 'scramble':
            ans = lobby['extra']['word'].lower().strip()
            if text.lower().strip() == ans:
                p = lobby['players'].get(user_id)
                p_name = p['name'] if p else "Player"
                xp = 20
                coins = 40
                del self.active_games[chat_id]
                return {
                    'correct': True,
                    'resolved': True,
                    'winner_name': p_name,
                    'winner_id': user_id,
                    'coins': coins,
                    'xp': xp,
                    'msg': f"✅ Correct! The word was **{ans.capitalize()}**! **{p_name}** wins **{coins} Coins** and **{xp} XP**! 🌟"
                }

        return None

# Singleton
game_manager = GameManager()
