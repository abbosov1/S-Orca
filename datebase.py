import sqlite3

conn = sqlite3.connect("dz.db")
cursor = conn.cursor()

# Создание таблиц пользователей
cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    user_id INTEGER PRIMARY KEY,
    fullname TEXT,
    age INTEGER,
    language TEXT,
    phone TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    question TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS forwarded_messages (
    user_id INTEGER NOT NULL,
    forwarded_message_id INTEGER NOT NULL,
    PRIMARY KEY (forwarded_message_id)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS contests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    start_date TEXT,
    end_date TEXT,
    status TEXT
)
""")
# Создание таблицы отзывов
cursor.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    review TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
# Создание таблицы отзывов
cursor.execute("""
CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL,
    timestamp DATETIME NOT NULL
)
""")
# Создадим таблицу tests, если её нет:
cursor.execute("""
CREATE TABLE IF NOT EXISTS tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    class TEXT,
    questions_ru TEXT,
    questions_uz TEXT,
    answers TEXT
)
""")
# Создадим таблицу tests, если её нет:
cursor.execute("""
CREATE TABLE IF NOT EXISTS tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    class TEXT,
    question_text_ru TEXT,
    question_text_uz TEXT,
    correct_answer TEXT,
    incorrect_answers TEXT
)
""")

conn.commit()

