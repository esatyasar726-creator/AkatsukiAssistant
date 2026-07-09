import sqlite3

DB_NAME = "akatsuki_bot.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            coins INTEGER DEFAULT 0,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            win_streak INTEGER DEFAULT 0
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
    conn.close()

def update_user_stats(user_id, username, coins=0, xp=0, win=True):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT coins, xp, level, win_streak FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result:
        c, x, l, s = result
        new_coins = c + coins
        new_xp = x + xp
        new_streak = s + 1 if win else 0
        # Simple level up logic: Level = sqrt(XP/100) + 1
        new_level = int((new_xp / 100) ** 0.5) + 1
        cursor.execute("UPDATE users SET coins = ?, xp = ?, level = ?, win_streak = ?, username = ? WHERE user_id = ?",
                       (new_coins, new_xp, new_level, new_streak, username, user_id))
    else:
        new_level = int((xp / 100) ** 0.5) + 1
        cursor.execute("INSERT INTO users (user_id, username, coins, xp, level, win_streak) VALUES (?, ?, ?, ?, ?, ?)",
                       (user_id, username, coins, xp, new_level, 1 if win else 0))

    conn.commit()
    conn.close()

def get_user_profile(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, coins, xp, level, win_streak FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_leaderboard(limit=10):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, coins, level FROM users ORDER BY coins DESC LIMIT ?", (limit,))
    results = cursor.fetchall()
    conn.close()
    return results

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
