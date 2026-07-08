import random

class GameManager:
    def __init__(self):
        # game_id -> {type, players, state, etc.}
        self.active_games = {}

    def start_math_challenge(self):
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        ops = ['+', '-', '*']
        op = random.choice(ops)

        if op == '+':
            answer = a + b
        elif op == '-':
            answer = a - b
        else:
            answer = a * b

        question = f"{a} {op} {b} = ?"
        return question, answer

    def start_dice_game(self, chat_id):
        # Initialize a lobby
        self.active_games[chat_id] = {
            'type': 'dice',
            'players': {}, # user_id -> {name, roll}
            'status': 'joining'
        }
        return "🎲 Dice Game Lobby Opened! Use /join to participate. (Wait 30s for the game to start)"

    def join_dice_game(self, chat_id, user_id, username):
        if chat_id in self.active_games and self.active_games[chat_id]['type'] == 'dice':
            if user_id not in self.active_games[chat_id]['players']:
                self.active_games[chat_id]['players'][user_id] = {'name': username, 'roll': None}
                return True
        return False

    def resolve_dice_game(self, chat_id):
        game = self.active_games.get(chat_id)
        if not game or game['type'] != 'dice':
            return None

        players = game['players']
        if not players:
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

        # If tie, just pick one for simplicity in this version
        winner_id = winners[0]
        winner_name = players[winner_id]['name']

        del self.active_games[chat_id]
        return results, winner_id, winner_name

    def start_emoji_guess(self):
        emojis = {
            "🍎": "apple", "🍌": "banana", "🚗": "car", "🏠": "house",
            "🐱": "cat", "🐶": "dog", "⚽": "football", "🍕": "pizza"
        }
        emoji = random.choice(list(emojis.keys()))
        answer = emojis[emoji]
        return emoji, answer

    def start_rps(self, chat_id, user1_id, user1_name):
        self.active_games[f"rps_{chat_id}"] = {
            'type': 'rps',
            'player1': {'id': user1_id, 'name': user1_name, 'choice': None},
            'player2': None # To be filled by /join_rps
        }
        return f"🤜 Akatsuki RPS! {user1_name} is waiting for an opponent. Use /join_rps to play!"

    def join_rps(self, chat_id, user2_id, user2_name):
        game_key = f"rps_{chat_id}"
        if game_key in self.active_games and self.active_games[game_key]['player2'] is None:
            if user2_id != self.active_games[game_key]['player1']['id']:
                self.active_games[game_key]['player2'] = {'id': user2_id, 'name': user2_name, 'choice': None}
                return True
        return False

    def start_quiz(self):
        quizzes = [
            {"q": "Who is the main protagonist of Bleach?", "a": "ichigo"},
            {"q": "What is the name of Ichigo's sword?", "a": "zangetsu"},
            {"q": "Who is the captain of the 6th Division?", "a": "byakuya"},
            {"q": "What is the final stage of a Zanpakuto?", "a": "bankai"},
            {"q": "Who is the creator of Bleach?", "a": "tite kubo"}
        ]
        quiz = random.choice(quizzes)
        return quiz['q'], quiz['a']

# Singleton
game_manager = GameManager()
