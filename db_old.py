import sqlite3

conn = sqlite3.connect("words.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS words (
    user_id INTEGER,
    word TEXT,
    translation TEXT,
    status TEXT
)
""")

conn.commit()