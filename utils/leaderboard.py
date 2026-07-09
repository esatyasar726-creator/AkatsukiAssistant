import json
import os

FILE = "data/leaderboard.json"


def load_scores():
    if not os.path.exists(FILE):
        with open(FILE, "w") as f:
            json.dump({}, f)

    with open(FILE, "r") as f:
        return json.load(f)


def save_scores(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)


def add_points(user_id, username, points):
    data = load_scores()

    uid = str(user_id)

    if uid not in data:
        data[uid] = {
            "username": username,
            "score": 0
        }

    data[uid]["username"] = username
    data[uid]["score"] += points

    save_scores(data)


def get_top():
    data = load_scores()

    ranking = sorted(
        data.values(),
        key=lambda x: x["score"],
        reverse=True
    )

    return ranking[:10]


def get_score(user_id):
    data = load_scores()
    uid = str(user_id)

    if uid not in data:
        return 0

    return data[uid]["score"]
