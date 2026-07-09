import random
import os
import json
import time

class GameManager:
    def __init__(self):
        self.active_games = {}
        self.trivia_db = self._load_json("data/questions/trivia.json", {"general": []})
        self.emoji_db = self._load_json("data/questions/emojis.json", [{"e": "🍎", "a": "apple"}])

    def _load_json(self, path, default):
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return default

    def start_lobby(self, chat_id, user_id, username, game_type):
        self.active_games[chat_id] = {
            'type': game_type,
            'players': {user_id: {'name': username, 'score': 0, 'roll': None}},
            'status': 'joining',
            'created_at': time.time(),
            'answer': None
        }
        return f"🎮 {username} started a {game_type.replace('_', ' ').title()}! Use /join to enter. (30s)"

    def join_lobby(self, chat_id, user_id, username):
        game = self.active_games.get(chat_id)
        if game and game['status'] == 'joining':
            if user_id not in game['players']:
                game['players'][user_id] = {'name': username, 'score': 0, 'roll': None}
                return True
        return False

    def start_math_challenge(self):
        a, b = random.randint(1, 100), random.randint(1, 100)
        op = random.choice(['+', '-', '*'])
        if op == '+': ans = a + b
        elif op == '-': ans = a - b
        else:
            a, b = random.randint(1, 20), random.randint(1, 20)
            ans = a * b
        return f"🧮 {a} {op} {b} = ?", str(ans)

    def start_trivia(self, category="general"):
        questions = self.trivia_db.get(category, self.trivia_db.get("general", []))
        if not questions: return "No questions found.", ""
        q = random.choice(questions)
        return q['q'], q['a']

    def start_emoji_guess(self):
        item = random.choice(self.emoji_db)
        return item['e'], item['a']

    def resolve_dice_duel(self, chat_id):
        game = self.active_games.pop(chat_id, None)
        if not game or not game['players']: return None

        results = []
        for uid, data in game['players'].items():
            data['roll'] = random.randint(1, 100) # Increased range for more excitement
            results.append(f"{data['name']}: {data['roll']}")

        winner_id = max(game['players'], key=lambda k: game['players'][k]['roll'])
        return results, winner_id, game['players'][winner_id]['name']

# Singleton
game_manager = GameManager()
