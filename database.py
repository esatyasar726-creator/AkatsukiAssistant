import sqlite3

DB_NAME = "users.db"


def connect():
    return sqlite3.connect(DB_NAME)


def setup_database():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leaderboard(
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        points INTEGER DEFAULT 0,
        correct INTEGER DEFAULT 0,
        wrong INTEGER DEFAULT 0,
        daily_played TEXT DEFAULT ''
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quiz_history(
        user_id INTEGER,
        question_id INTEGER
    )
    """)

    conn.commit()
    conn.close()


def add_points(user_id, username, amount):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM leaderboard WHERE user_id=?",
        (user_id,)
    )

    row = cursor.fetchone()

    if row is None:

        cursor.execute("""
        INSERT INTO leaderboard
        (user_id, username, points, correct, wrong)
        VALUES (?, ?, ?, 0, 0)
        """,
        (user_id, username, amount))

    else:

        cursor.execute("""
        UPDATE leaderboard
        SET points = points + ?
        WHERE user_id = ?
        """,
        (amount, user_id))

    conn.commit()
    conn.close()
