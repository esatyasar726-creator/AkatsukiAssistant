import sqlite3
from datetime import datetime, timedelta

DB_NAME = "akatsuki_bot.db"

# Map level to Bleach Rank names for prestige feel
RANKS = {
    1: "Rookie",
    3: "Soul Cadet",
    5: "Seated Officer",
    10: "Lieutenant",
    15: "Captain",
    20: "Royal Guard",
    25: "Head Captain",
    30: "Soul King"
}

def get_rank_for_level(lvl):
    active_rank = "Rookie"
    for threshold, rname in sorted(RANKS.items()):
        if lvl >= threshold:
            active_rank = rname
    return active_rank

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 1. Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            score INTEGER DEFAULT 0,
            coins INTEGER DEFAULT 100,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            rank TEXT DEFAULT 'Rookie',
            achievements TEXT DEFAULT '[]',
            daily_streak INTEGER DEFAULT 0,
            last_daily TEXT DEFAULT '',
            win_streak INTEGER DEFAULT 0,
            games_played INTEGER DEFAULT 0,
            games_won INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_members (
            chat_id INTEGER,
            user_id INTEGER,
            username TEXT,
            PRIMARY KEY (chat_id, user_id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminder_settings (
            chat_id INTEGER PRIMARY KEY,
            enabled INTEGER DEFAULT 0,
            lead_minutes INTEGER DEFAULT 15
        )
    """)
    conn.commit()

    # 2. Migration: Add columns to existing DB tables if they don't exist
    columns_to_add = [
        ("coins", "INTEGER DEFAULT 100"),
        ("xp", "INTEGER DEFAULT 0"),
        ("level", "INTEGER DEFAULT 1"),
        ("rank", "TEXT DEFAULT 'Rookie'"),
        ("achievements", "TEXT DEFAULT '[]'"),
        ("daily_streak", "INTEGER DEFAULT 0"),
        ("last_daily", "TEXT DEFAULT ''"),
        ("win_streak", "INTEGER DEFAULT 0"),
        ("games_played", "INTEGER DEFAULT 0"),
        ("games_won", "INTEGER DEFAULT 0")
    ]
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            conn.commit()
        except sqlite3.OperationalError:
            # Column already exists, safe to ignore
            pass

    conn.close()

def update_score(user_id, username, points):
    # Backward compatibility with existing score scoring
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        new_score = result[0] + points
        cursor.execute("UPDATE users SET score = ?, username = ? WHERE user_id = ?", (new_score, username, user_id))
    else:
        cursor.execute("INSERT INTO users (user_id, username, score) VALUES (?, ?, ?)", (user_id, username, points))
        new_score = points
    conn.commit()
    conn.close()
    return new_score

def get_user_score(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def get_user_profile(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, score, coins, xp, level, rank, achievements, daily_streak, win_streak, games_played, games_won
        FROM users WHERE user_id = ?
    """, (user_id,))
    res = cursor.fetchone()
    conn.close()
    if res:
        import json
        return {
            "username": res[0], "score": res[1], "coins": res[2], "xp": res[3],
            "level": res[4], "rank": res[5], "achievements": json.loads(res[6] or '[]'),
            "daily_streak": res[7], "win_streak": res[8], "games_played": res[9], "games_won": res[10]
        }
    return None

def add_rewards(user_id, username, coins_reward, xp_reward, won=False):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT score, coins, xp, level, games_played, games_won, win_streak FROM users WHERE user_id = ?
    """, (user_id,))
    res = cursor.fetchone()

    leveled_up = False
    new_lvl = 1

    if res:
        score_val, coins, xp, lvl, gp, gw, ws = res
        new_score = score_val + int(xp_reward / 2) # legacy score tracker correlation
        new_coins = coins + coins_reward
        new_xp = xp + xp_reward
        new_gp = gp + 1
        new_gw = gw + 1 if won else gw
        new_ws = ws + 1 if won else 0

        # Calculate level up
        # formula: xp needed to level up = lvl * 150
        while new_xp >= (lvl * 150):
            new_xp -= (lvl * 150)
            lvl += 1
            leveled_up = True

        new_lvl = lvl
        new_rank = get_rank_for_level(lvl)

        cursor.execute("""
            UPDATE users SET score = ?, coins = ?, xp = ?, level = ?, rank = ?,
                             games_played = ?, games_won = ?, win_streak = ?, username = ?
            WHERE user_id = ?
        """, (new_score, new_coins, new_xp, lvl, new_rank, new_gp, new_gw, new_ws, username, user_id))
    else:
        new_score = int(xp_reward / 2)
        new_coins = 100 + coins_reward
        new_xp = xp_reward
        lvl = 1
        while new_xp >= (lvl * 150):
            new_xp -= (lvl * 150)
            lvl += 1
            leveled_up = True
        new_lvl = lvl
        new_rank = get_rank_for_level(lvl)

        cursor.execute("""
            INSERT INTO users (user_id, username, score, coins, xp, level, rank, games_played, games_won, win_streak)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username, new_score, new_coins, new_xp, lvl, new_rank, 1, 1 if won else 0, 1 if won else 0))

    conn.commit()
    conn.close()
    return leveled_up, new_lvl, new_rank

def claim_daily(user_id, username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT coins, daily_streak, last_daily FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()

    now_str = datetime.utcnow().strftime("%Y-%m-%d")

    if res:
        coins, streak, last_daily = res
        if last_daily == now_str:
            conn.close()
            return False, "❌ You have already claimed your daily reward today! Come back tomorrow. 🕒"

        # Check if yesterday was claimed to keep streak
        # Simple date diff check
        streak_maintained = False
        if last_daily:
            try:
                ld_date = datetime.strptime(last_daily, "%Y-%m-%d")
                if (datetime.utcnow() - ld_date).days <= 1:
                    streak_maintained = True
            except ValueError:
                pass

        new_streak = (streak + 1) if streak_maintained or not last_daily else 1
        reward = 100 + (new_streak * 10) # streak bonus
        new_coins = coins + reward

        cursor.execute("""
            UPDATE users SET coins = ?, daily_streak = ?, last_daily = ?, username = ? WHERE user_id = ?
        """, (new_coins, new_streak, now_str, username, user_id))
    else:
        new_streak = 1
        reward = 100
        cursor.execute("""
            INSERT INTO users (user_id, username, coins, daily_streak, last_daily)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, username, 100 + reward, new_streak, now_str))

    conn.commit()
    conn.close()
    return True, f"🎁 **Daily Reward Claimed!**\n\nEarned: **{reward} Coins** 🪙\nStreak: **{new_streak} days** 🔥"

def get_leaderboard(limit=10):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, score FROM users ORDER BY score DESC LIMIT ?", (limit,))
    results = cursor.fetchall()
    conn.close()
    return results

def get_coins_leaderboard(limit=10):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, coins FROM users ORDER BY coins DESC LIMIT ?", (limit,))
    results = cursor.fetchall()
    conn.close()
    return results

def unlock_achievement(user_id, ach_name):
    import json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT achievements, coins FROM users WHERE user_id = ?", (user_id,))
    res = cursor.fetchone()

    unlocked = False
    if res:
        ach_list = json.loads(res[0] or '[]')
        coins = res[1]
        if ach_name not in ach_list:
            ach_list.append(ach_name)
            new_coins = coins + 100 # achievement coin reward
            cursor.execute("UPDATE users SET achievements = ?, coins = ? WHERE user_id = ?", (json.dumps(ach_list), new_coins, user_id))
            unlocked = True
    conn.commit()
    conn.close()
    return unlocked

def add_chat_member(chat_id, user_id, username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO chat_members (chat_id, user_id, username) VALUES (?, ?, ?)", (chat_id, user_id, username))
    conn.commit()
    conn.close()

def remove_chat_member(chat_id, user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM chat_members WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
    conn.commit()
    conn.close()

def get_chat_members(chat_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username FROM chat_members WHERE chat_id = ?", (chat_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def set_reminder_enabled(chat_id, enabled):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reminder_settings (chat_id, enabled) VALUES (?, ?) ON CONFLICT(chat_id) DO UPDATE SET enabled = EXCLUDED.enabled", (chat_id, 1 if enabled else 0))
    conn.commit()
    conn.close()

def set_reminder_lead(chat_id, minutes):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reminder_settings (chat_id, lead_minutes) VALUES (?, ?) ON CONFLICT(chat_id) DO UPDATE SET lead_minutes = EXCLUDED.lead_minutes", (chat_id, minutes))
    conn.commit()
    conn.close()

def get_reminder_settings(chat_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT enabled, lead_minutes FROM reminder_settings WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (0, 15)

def get_all_chats_with_reminders():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id, lead_minutes FROM reminder_settings WHERE enabled = 1")
    results = cursor.fetchall()
    conn.close()
    return results
