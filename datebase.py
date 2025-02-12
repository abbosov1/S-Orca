import sqlite3

conn = sqlite3.connect("dz.db")
cursor = conn.cursor()

# Создание таблиц user
cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    user_id INTEGER PRIMARY KEY,
    fullname TEXT,
    age INTEGER,
    language TEXT,
    phone TEXT
)
""")
# Создание таблицы questions
cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    question TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
# Создание таблицы forwarded_messages
cursor.execute("""
CREATE TABLE IF NOT EXISTS forwarded_messages (
    user_id INTEGER NOT NULL,
    forwarded_message_id INTEGER NOT NULL,
    PRIMARY KEY (forwarded_message_id)
)
""")
# Создание таблицы contests
cursor.execute("""
CREATE TABLE IF NOT EXISTS contests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    start_date TEXT,
    end_date TEXT,
    status TEXT
)
""")
# Создание таблицы reviews
cursor.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    review TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

