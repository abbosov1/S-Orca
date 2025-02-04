import logging
import sqlite3
from aiogram import *
from aiogram.filters import StateFilter
from aiogram.types import (Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton,
                           ReactionTypeEmoji, CallbackQuery, ReplyKeyboardRemove)
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Константы
TOKEN = "6486958358:AAG3Txo1kM5g_4tz5VjKrSqWrsYDYFJciWY"
ADMIN_ID = 5445669072  # Укажите ваш Telegram ID

# Инициализация бота и диспетчера
bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=MemoryStorage())

# Подключение к базе данных SQLite
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

conn.commit()


# Состояния пользователя
class UserStates(StatesGroup):
    waiting_for_review = State()
    waiting_for_contest_dates = State()
    waiting_for_contest_title = State()
    waiting_for_language = State()
    waiting_for_fullname = State()
    waiting_for_class = State()


# Новые состояния для создания тестов
class AdminTestCreationStates(StatesGroup):
    choosing_subject = State()  # Выбор предмета
    choosing_class = State()  # Выбор класса
    waiting_for_question = State()  # Ожидание ввода текста вопроса
    waiting_for_correct_answer = State()  # Ожидание ввода правильного ответа
    waiting_for_incorrect_answers = State()  # Ожидание ввода неправильных ответов


# Кнопки для выбора языка
language_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="O'zbek tili", callback_data="lang_uz"),
            InlineKeyboardButton(text="Русский язык", callback_data="lang_ru")
        ]
    ]
)

# Главное меню на двух языках
main_menu = {
    "uz": ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Uyga vazifaga yordam"), KeyboardButton(text="Olimpiadalar 🔥")],
            [KeyboardButton(text="Adminstratorga savol"), KeyboardButton(text="Mening ma'lumotlarim")],
            [KeyboardButton(text="Fikr bildirish ✍️"), KeyboardButton(text="Sozlamalar")],
        ],
        resize_keyboard=True
    ),
    "ru": ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Помощь с домашним заданием"), KeyboardButton(text="Конкурсы 🔥")],
            [KeyboardButton(text="Вопрос к администратору"), KeyboardButton(text="Мои данные")],
            [KeyboardButton(text="Оставить отзыв ✍️"), KeyboardButton(text="Настройки")],
        ],
        resize_keyboard=True
    )
}
admin_menu = {
    "uz": ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Foydalanuvchilar ro'yxati"), KeyboardButton(text="Olimpiadalar qo'shish")],
        ],
        resize_keyboard=True

    ),
    "ru": ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Список пользователей"), KeyboardButton(text="Добавить конкурсы")],
        ],
        resize_keyboard=True
    )
}
settings_menu = {
    "ru": ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Изменить язык")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    ),
    "uz": ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Tilni o'zgartirish")],
            [KeyboardButton(text="Orqaga")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
}

# Клавиатура для ответа на вопрос «У вас есть ещё вопросы?»
feedback_reply = {
    "ru": ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Да")],
            [KeyboardButton(text="Нет")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    ),
    "uz": ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Ha")],
            [KeyboardButton(text="Yo'q")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
}
# Клавиатура для ответа на вопрос «subject_keyboard»
subject_keyboard = {
    "ru": ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Английский язык")],
            [KeyboardButton(text="Русский язык")],
            [KeyboardButton(text="Математика")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    ),
    "uz": ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Ingliz tili")],
            [KeyboardButton(text="Rus tili")],
            [KeyboardButton(text="Matematika")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
}
# Клавиатура для ответа на вопрос «class_keyboard»
class_keyboard = {
    "ru": ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1 класс"), KeyboardButton(text="2 класс")],
            [KeyboardButton(text="3 класс"), KeyboardButton(text="4 класс")],
            [KeyboardButton(text="5 класс"), KeyboardButton(text="6 класс")],
            [KeyboardButton(text="7 класс"), KeyboardButton(text="8 класс")],
            [KeyboardButton(text="9 класс"), KeyboardButton(text="10 класс")],
            [KeyboardButton(text="11 класс")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    ),
    "uz": ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1-sinf"), KeyboardButton(text="2-sinf")],
            [KeyboardButton(text="3-sinf"), KeyboardButton(text="4-sinf")],
            [KeyboardButton(text="5-sinf"), KeyboardButton(text="6-sinf")],
            [KeyboardButton(text="7-sinf"), KeyboardButton(text="8-sinf")],
            [KeyboardButton(text="9-sinf"), KeyboardButton(text="10-sinf")],
            [KeyboardButton(text="11-sinf")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
}
# Клавиатура для ответа на вопрос «subject_menu»
subject_menu = {
    "ru": ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Английский язык")],
            [KeyboardButton(text="Русский язык")],
            [KeyboardButton(text="Математика")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    ),
    "uz": ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Ingliz tili")],
            [KeyboardButton(text="Rus tili")],
            [KeyboardButton(text="Matematika")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
}

# Клавиатура для оценки (5 кнопок)
rating_keyboard = {
    "ru": ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1 ⭐")],
            [KeyboardButton(text="2 ⭐")],
            [KeyboardButton(text="3 ⭐")],
            [KeyboardButton(text="4 ⭐")],
            [KeyboardButton(text="5 ⭐")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    ),
    "uz": ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1 ⭐")],
            [KeyboardButton(text="2 ⭐")],
            [KeyboardButton(text="3 ⭐")],
            [KeyboardButton(text="4 ⭐")],
            [KeyboardButton(text="5 ⭐")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
}


@dp.message(Command("state"))  # /state
async def check_state(message: Message, state: FSMContext):
    current_state = await state.get_state()
    await message.answer(f"Текущее состояние: {current_state}")
    print(f"[LOG] Состояние FSM: {current_state}")


# Команда /start
@dp.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    user_id = message.from_user.id

    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))

    if user_id == ADMIN_ID:
        cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
        user_data = cursor.fetchone()

        if user_data:
            language = user_data[0]
            await message.answer(
                "Добро пожаловать, администратор!" if language == "ru" else "Xush kelibsiz, administrator!",
                reply_markup=admin_menu[language]
            )
        else:
            await message.answer(
                "Привет, добро пожаловать в бота! Выберите язык:" if message.from_user.language_code == "ru"
                else "Assalomu alaykum, botga xush kelibsiz! Tilni tanlang:",
                reply_markup=language_keyboard
            )
            await state.set_state(UserStates.waiting_for_language)

    else:
        cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
        user_data = cursor.fetchone()

        if user_data:
            language = user_data[0]
            await message.answer(
                "Добро пожаловать!" if language == "ru" else "Xush kelibsiz!",
                reply_markup=main_menu[language]
            )
        else:
            await message.answer(
                "Привет, добро пожаловать в бота! Выберите язык:" if message.from_user.language_code == "ru"
                else "Assalomu alaykum, botga xush kelibsiz! Tilni tanlang:",
                reply_markup=language_keyboard
            )
            await state.set_state(UserStates.waiting_for_language)


# Обработка выбора языка и запроса номера телефона
@dp.callback_query(lambda call: call.data.startswith("lang_"))
async def language_selected(call: CallbackQuery):
    user_id = call.from_user.id
    selected_language = "ru" if call.data == "lang_ru" else "uz"
    cursor.execute("INSERT INTO user (user_id, language) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET language = ?",
                   (user_id, selected_language, selected_language))
    conn.commit()

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить мой номер", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await call.message.answer(
        "Отправьте свой номер телефона:" if selected_language == "ru" else "Telefon raqamingizni yuboring:",
        reply_markup=keyboard
    )
    await call.answer()  # Обработка номера телефона


@dp.message(lambda message: message.contact)
async def phone_received(message: Message, state: FSMContext):
    user_id = message.from_user.id
    phone_number = message.contact.phone_number
    cursor.execute("UPDATE user SET phone = ? WHERE user_id = ?", (phone_number, user_id))
    conn.commit()

    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    language = cursor.fetchone()[0]

    await message.answer(
        "Введите ваше имя:" if language == "ru" else "Ismingizni kiriting:"
    )
    await state.set_state(UserStates.waiting_for_fullname)


# Обработка имени пользователя
@dp.message(UserStates.waiting_for_fullname)
async def process_fullname(message: Message, state: FSMContext):
    fullname = message.text
    user_id = message.from_user.id

    cursor.execute("UPDATE user SET fullname = ? WHERE user_id = ?", (fullname, user_id))
    conn.commit()

    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    language = cursor.fetchone()[0]

    await message.answer(
        "Спасибо! Теперь введите ваш класс (1-11):" if language == "ru"
        else "Rahmat! Endi sinfingizni kiriting (1-11):"
    )
    await state.set_state(UserStates.waiting_for_class)


# Обработка класса пользователя
@dp.message(UserStates.waiting_for_class)
async def process_class(message: Message, state: FSMContext):
    user_id = message.from_user.id
    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    language = cursor.fetchone()[0]
    try:
        age = int(message.text)
        if 1 <= age <= 11:
            cursor.execute("UPDATE user SET age = ? WHERE user_id = ?", (age, user_id))
            conn.commit()

            await message.answer(
                "Ваши данные успешно сохранены. Выберите действие из меню:" if language == "ru"
                else "Ma'lumotlaringiz muvaffaqiyatli saqlandi. Menyudan amalni tanlang:",
                reply_markup=main_menu[language]
            )
            await state.clear()
        else:
            await message.answer(
                "Пожалуйста, введите корректный класс (1-11)." if language == "ru"
                else "Iltimos, to'g'ri sinfni kiriting (1-11)."
            )
    except ValueError:
        cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
        language = cursor.fetchone()[0]

        await message.answer(
            "Пожалуйста, введите номер класса (1-11) цифрами." if language == "ru"
            else "Iltimos, sinf raqamini (1-11) raqamlarda kiriting."
        )


# Функция для получения языка пользователя
def get_user_language(user_id: int) -> str:
    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else "ru"


# Обработка кнопки "Конкурсы 🔥"
@dp.message(lambda message: message.text in ["Конкурсы 🔥", "Olimpiadalar 🔥"])
async def show_contests(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    language = cursor.fetchone()[0]

    cursor.execute("SELECT title, start_date, end_date FROM contests WHERE status = 'active'")
    active_contests = cursor.fetchall()

    if active_contests:
        text = "📢 *Текущие конкурсы:*\n\n" if language == "ru" else "📢 *Hozirgi olimpiadalar:*\n\n"
        for contest in active_contests:
            text += f"📌 *{contest[0]}*\n📅 {contest[1]} - {contest[2]}\n\n"
    else:
        text = "Конкурсы скоро начнутся, пока что приготовьтесь!" if language == "ru" \
            else "Olimpiadalar tez orada boshlanadi, hozircha tayyorlaning!"

    await message.answer(text, parse_mode="Markdown")


# Обработка кнопки "Добавить конкурсы" (только для админа)
@dp.message(lambda message: message.text in ["Добавить конкурсы", "Olimpiadalar qo'shish"])
async def add_contest(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    user_id = message.from_user.id
    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    language = cursor.fetchone()[0]

    await message.answer(
        "Введите название конкурса:" if language == "ru" else "Olimpiada nomini kiriting:"
    )
    await state.set_state(UserStates.waiting_for_contest_title)


# Ввод названия конкурса
@dp.message(UserStates.waiting_for_contest_title)
async def contest_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    user_id = message.from_user.id
    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    language = cursor.fetchone()[0]

    await message.answer(
        "Введите период проведения (например: 01.02.2025 - 15.02.2025):" if language == "ru"
        else "O'tkazilish davrini kiriting (masala n: 01.02.2025 - 15.02.2025):"
    )
    await state.set_state(UserStates.waiting_for_contest_dates)


# Ввод периода проведения
@dp.message(UserStates.waiting_for_contest_dates)
async def contest_dates(message: Message, state: FSMContext):
    data = await state.get_data()
    title = data["title"]
    dates = message.text.split("-")

    if len(dates) != 2:
        await message.answer("❌ Неправильный формат! Попробуйте ещё раз.")
        return

    start_date, end_date = dates[0].strip(), dates[1].strip()
    cursor.execute("INSERT INTO contests (title, start_date, end_date, status) VALUES (?, ?, ?, 'active')",
                   (title, start_date, end_date))
    conn.commit()

    await message.answer("✅ Конкурс добавлен!")
    await state.clear()


# Обработка кнопки "Оставить отзыв ✍️"
@dp.message(lambda message: message.text in ["Оставить отзыв ✍️", "Fikr bildirish ✍️"])
async def leave_review(message: Message, state: FSMContext):
    user_id = message.from_user.id
    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    language = cursor.fetchone()[0]

    await message.answer(
        "Оставьте свой отзыв ✍️:" if language == "ru" else "Fikringizni qoldiring ✍️:"
    )
    await state.set_state(UserStates.waiting_for_review)


# Обработка отзыва
@dp.message(UserStates.waiting_for_review)
async def process_review(message: Message, state: FSMContext):
    user_id = message.from_user.id
    review_text = message.text

    # Сохраняем отзыв в базу данных
    cursor.execute("INSERT INTO reviews (user_id, review) VALUES (?, ?)", (user_id, review_text))
    conn.commit()

    # Ставим реакцию 👍
    await message.react([ReactionTypeEmoji(emoji="👍")])

    # Отправляем ответ
    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    language = cursor.fetchone()[0]
    await message.answer(
        "Спасибо за ваш отзыв 🤝" if language == "ru" else "Fikringiz uchun rahmat 🤝"
    )

    # Очищаем состояние
    await state.clear()


# Обработка команды "Отправить картинку"
@dp.message(lambda message: message.text in ["Помощь с домашним заданием", "Uyga vazifaga yordam"])
async def homework_help(message: Message, state: FSMContext):
    user_id = message.from_user.id

    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    user_language = cursor.fetchone()
    if user_language:
        user_language = user_language[0]
    else:
        user_language = "ru"  # Если язык не найден, по умолчанию — русский

    # Просим отправить фото
    text = "Хорошо, отправьте фото для обработки." if user_language == "ru" else "Yaxshi, rasmni yuboring."
    await message.answer(text)

    # Ставим состояние ожидания фото
    await state.set_state("waiting_for_homework_photo")


@dp.message(StateFilter("waiting_for_homework_photo"),
            lambda message: message.photo and message.from_user.id != ADMIN_ID)
async def receive_homework_photo(message: Message, state: FSMContext):
    user_id = message.from_user.id

    # Сохраняем photo_id во временное состояние
    await state.update_data(photo_id=message.photo[-1].file_id)

    # Получаем язык пользователя
    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    user_language = result[0] if result else "ru"

    # Просим написать вопрос к картинке
    text = (
        "Хорошо, напишите свой вопрос по этой картинке или скажите, что надо сделать с ней."
        if user_language == "ru"
        else "Yaxshi, ushbu rasm bilan bog'liq savolingizni yozing yoki nima qilish kerakligini tushuntiring."
    )
    await message.answer(text)

    # Ставим состояние ожидания вопроса
    await state.set_state("waiting_for_homework_question")


@dp.message(StateFilter("waiting_for_homework_question"))
async def receive_homework_question(message: Message, state: FSMContext):
    user_id = message.from_user.id

    # Получаем язык пользователя
    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    user_language = result[0] if result else "ru"

    # Получаем сохранённое фото
    data = await state.get_data()
    photo_id = data.get("photo_id")

    # Формируем подпись для администратора в зависимости от типа вопроса
    if message.text:
        # Если вопрос текстовый
        question_text = message.text
        caption = (
            f"Вопрос по домашнему заданию от пользователя {user_id}:\n\n{question_text}"
            if user_language == "ru"
            else f"Foydalanuvchidan {user_id} uyga vazifa bo'yicha savol:\n\n{question_text}"
        )
        admin_message = await bot.send_photo(ADMIN_ID, photo_id, caption=caption)
    elif message.voice:
        # Если вопрос голосовой
        caption = (
            f"Вопрос по домашнему заданию от пользователя {user_id}: голосовое сообщение"
            if user_language == "ru"
            else f"Foydalanuvchidan {user_id} uyga vazifa bo'yicha savol: ovozli xabar"
        )
        # Отправляем фото с подписью
        admin_message = await bot.send_photo(ADMIN_ID, photo_id, caption=caption)
        # Отправляем само голосовое сообщение
        await bot.send_voice(ADMIN_ID, message.voice.file_id)
    else:
        error_text = (
            "Пожалуйста, отправьте текст или голосовое сообщение с вопросом."
            if user_language == "ru"
            else "Iltimos, savolingizni matn yoki ovozli xabar ko‘rinishida yuboring."
        )
        await message.answer(error_text)
        return

    # Сохраняем в базу данных связь между ID сообщения, отправленного админу, и ID пользователя
    cursor.execute(
        "INSERT INTO forwarded_messages (user_id, forwarded_message_id) VALUES (?, ?)",
        (user_id, admin_message.message_id)
    )
    conn.commit()

    # Сообщаем пользователю, что вопрос отправлен
    confirmation_text = (
        "Ваш вопрос был отправлен администратору. Пожалуйста, ожидайте ответа."
        if user_language == "ru"
        else "Savolingiz administratorga yuborildi. Iltimos, javobni kuting."
    )
    await message.answer(confirmation_text)

    # Очищаем состояние
    await state.clear()


# Обработчик команд администратора (отдельно от обычных сообщений)
@dp.message(lambda message: message.from_user.id == ADMIN_ID and message.text in [
    "Список пользователей", "Foydalanovchilar ro'yhati",
    "Добавить тесты", "Testlarni qo'shish"
])
async def handle_admin_commands(message: Message, state: FSMContext):
    if message.text in ["Список пользователей", "Foydalanovchilar ro'yhati"]:
        await list_users(message)
    elif message.text in ["Добавить тесты", "Testlarni qo'shish"]:
        await add_tests_start(message, state)


# Обработчик обычных сообщений администратора (ответ пользователям)
@dp.message(StateFilter(None), lambda message: message.from_user.id == ADMIN_ID)
async def handle_admin_message(message: Message):
    # Проверяем, является ли сообщение командой — если да, выходим
    admin_commands = ["Список пользователей", "Foydalanovchilar ro'yhati", "Добавить тесты", "Testlarni qo'shish"]
    if message.text in admin_commands:
        return

    # Ищем пользователя, связанного с этим сообщением
    cursor.execute(
        "SELECT user_id FROM forwarded_messages WHERE forwarded_message_id = ?",
        (message.reply_to_message.message_id,)
    )
    result = cursor.fetchone()

    if result:
        original_sender_id = result[0]
        logging.info(f"Администратор отвечает пользователю {original_sender_id}")

        # Получаем язык пользователя
        cursor.execute("SELECT language FROM user WHERE user_id = ?", (original_sender_id,))
        language_result = cursor.fetchone()
        language = language_result[0] if language_result else "ru"

        # Формируем текст ответа (для текстового сообщения)
        if message.text:
            reply_text = (
                f"Ответ от администратора: \n\n{message.text}\n\n"
                f"Этот бот работает 24/7. Вы можете отправить картинку для "
                f"обработки или задать вопрос, нажав кнопку 'Вопрос к администратору'."
                if language == "ru"
                else f"Adminstratordan javob: \n\n{message.text}\n\n"
                     f"Bu bot 24/7 ishlaydi. Rasmlarni yuboring yoki "
                     f"'Adminstratorga savol' tugmasini bosib, savolingizni yuboring."
            )
            await bot.send_message(original_sender_id, reply_text, reply_markup=main_menu[language])

        # Ответ с фотографией
        elif message.photo:
            await bot.send_photo(
                original_sender_id,
                message.photo[-1].file_id,
                caption=(f"Ответ администратора: {message.caption or 'Без текста'}\n\nЭтот бот работает 24/7. "
                         f"Вы можете отправить картинку для обработки или задать вопрос, "
                         f"нажав кнопку 'Вопрос к администратору'."
                         if language == "ru"
                         else f"Adminstratordan javob: {message.caption or 'Matn yo\'q'}\n\nBu bot 24/7 ishlaydi. "
                              f"Rasmlarni yuboring yoki 'Adminstratorga savol' "
                              f"tugmasini bosib, savolingizni yuboring."),
                reply_markup=main_menu[language]
            )

        # Ответ с голосовым сообщением
        elif message.voice:
            await bot.send_voice(
                original_sender_id,
                message.voice.file_id,
                caption=("Этот бот работает 24/7. У вас есть еще вопросы? "
                         "Вы можете подать заявку, если у вас снова возникнут трудности."
                         if language == "ru"
                         else "Bu bot 24/7 ishlaydi. Yana savollaringiz bormi? "
                              "Yana muammo yuzaga kelsa, murojaat qilishingiz mumkin."),
                reply_markup=main_menu[language]
            )

        # Ответ с видеосообщением
        elif message.video:
            await bot.send_video(
                original_sender_id,
                message.video.file_id,
                caption=("Этот бот работает 24/7. У вас есть еще вопросы? "
                         "Вы можете подать заявку, если у вас снова возникнут трудности."
                         if language == "ru"
                         else "Bu bot 24/7 ishlaydi. Yana savollaringiz bormi? "
                              "Yana muammo yuzaga kelsa, murojaat qilishingiz mumkin."),
                reply_markup=main_menu[language]
            )

        # Ответ с файлом
        elif message.document:
            await bot.send_document(
                original_sender_id,
                message.document.file_id,
                caption=("Этот бот работает 24/7. У вас есть еще вопросы? "
                         "Вы можете подать заявку, если у вас снова возникнут трудности."
                         if language == "ru"
                         else "Bu bot 24/7 ishlaydi. Yana savollaringiz bormi? "
                              "Yana muammo yuzaga kelsa, murojaat qilishingiz mumkin."),
                reply_markup=main_menu[language]
            )

        await message.reply("Ваш ответ был отправлен пользователю." if language == "ru"
                            else "Javobingiz foydalanuvchiga yuborildi.")

        # После отправки ответа – отправляем пользователю запрос:
        # «У вас есть ещё вопросы?» с двумя кнопками (Да/Нет)
        followup_text = "У вас есть ещё вопросы?" if language == "ru" else "Sizda yana savollar bormi?"
        await bot.send_message(original_sender_id, followup_text, reply_markup=feedback_reply[language])

        await message.reply("Ваш ответ был отправлен пользователю." if language == "ru"
                            else "Javobingiz foydalanuvchiga yuborildi.")
    else:
        await message.reply("Ошибка: не удалось найти отправителя сообщения.")


# Обработка команды "Вопрос к администратору"
@dp.message(lambda message: message.text in ["Вопрос к администратору", "Adminstratorga savol"])
async def handle_questions(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # Получаем выбранный язык пользователя из базы данных
    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    user_language = cursor.fetchone()
    if user_language:
        user_language = user_language[0]
    else:
        user_language = "ru"  # Если язык не найден, по умолчанию — русский

    # Информируем пользователя о том, что можно отправлять как текст, так и голосовое сообщение
    if user_language == "uz":
        await message.answer(
            "Yaxshi, savollaringizni matn yoki ovozli xabar ko‘rinishida "
            "yuborishingiz mumkin, men ularni administratorga yuboraman.")
    else:
        await message.answer(
            "Хорошо, вы можете отправить свой вопрос в виде текста или "
            "голосового сообщения, и я передам его администратору.")

    # Устанавливаем состояние ожидания вопроса
    await state.set_state("waiting_for_question")


# ---------------------------
# Обработка вопроса пользователя (текст или голос)
@dp.message(StateFilter("waiting_for_question"))
async def process_question(message: Message, state: FSMContext):
    user_id = message.from_user.id
    # Получаем выбранный язык пользователя из базы данных
    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    user_language = result[0] if result else "ru"

    # Обработка текстового сообщения
    if message.text:
        if user_language == "uz":
            forwarded_message = await bot.send_message(
                ADMIN_ID,
                f"Foydalanuvchidan savol: {user_id}\n\n{message.text}",
            )
            await message.answer("Savolingiz administratorga yuborildi. Iltimos, javobni kuting.")
        else:
            forwarded_message = await bot.send_message(
                ADMIN_ID,
                f"Вопрос от пользователя {user_id}:\n\n{message.text}",
            )
            await message.answer("Ваш вопрос был передан администратору. Пожалуйста, ожидайте ответа.")

    # Обработка голосового сообщения
    elif message.voice:
        if user_language == "uz":
            caption = f"Foydalanuvchidan savol: {user_id} (ovozli xabar)"
            forwarded_message = await bot.send_voice(
                ADMIN_ID,
                message.voice.file_id,
                caption=caption
            )
            await message.answer("Savolingiz administratorga yuborildi. Iltimos, javobni kuting.")
        else:
            caption = f"Вопрос от пользователя {user_id}: (голосовое сообщение)"
            forwarded_message = await bot.send_voice(
                ADMIN_ID,
                message.voice.file_id,
                caption=caption
            )
            await message.answer("Ваш вопрос был передан администратору. Пожалуйста, ожидайте ответа.")
    else:
        error_text = (
            "Пожалуйста, отправьте текст или голосовое сообщение."
            if user_language == "ru"
            else "Iltimos, matn yoki ovozli xabar yuboring."
        )
        await message.answer(error_text)
        return

    # Сохранение ID пересланного сообщения и ID пользователя в базе данных
    cursor.execute(
        "INSERT INTO forwarded_messages (forwarded_message_id, user_id) VALUES (?, ?)",
        (forwarded_message.message_id, user_id)
    )
    conn.commit()

    # Очистить состояние
    await state.clear()


# ---------------------------
# Обработка ответа администратора (поддержка текстовых и голосовых сообщений)
@dp.message(lambda message: message.chat.id == ADMIN_ID)
async def handle_admin_reply(message: Message):
    if not message.reply_to_message:
        return await message.reply("Пожалуйста, ответьте на сообщение пользователя, чтобы связать ответ с вопросом.")

    # Ищем пользователя, связанного с данным сообщением, по базе пересланных сообщений
    forwarded_message_id = message.reply_to_message.message_id
    cursor.execute(
        "SELECT user_id FROM forwarded_messages WHERE forwarded_message_id = ?",
        (forwarded_message_id,)
    )
    result = cursor.fetchone()
    if not result:
        return await message.reply("Ошибка: не удалось найти отправителя сообщения.")

    original_user_id = result[0]
    # Обновляем запись, если необходимо (например, сброс флага вопроса)
    cursor.execute("UPDATE user SET question_sent = 0 WHERE user_id = ?", (original_user_id,))
    conn.commit()

    # Получаем язык пользователя для формирования ответа
    cursor.execute("SELECT language FROM user WHERE user_id = ?", (original_user_id,))
    lang_result = cursor.fetchone()
    language = lang_result[0] if lang_result else "ru"

    # Формируем и отправляем ответ пользователю в зависимости от типа сообщения
    if message.text:
        await bot.send_message(
            original_user_id,
            f"Ответ от администратора:\n\n{message.text}")
    elif message.voice:
        await bot.send_voice(
            original_user_id,
            message.voice.file_id,
            caption="Ответ от администратора:")
    elif message.photo:
        await bot.send_photo(
            original_user_id,
            message.photo[-1].file_id,
            caption=f"Ответ от администратора: {message.caption or 'Без текста'}")
    else:
        await bot.send_message(
            original_user_id,
            "Ответ от администратора получен.")

    await message.reply("Ваш ответ был отправлен пользователю." if language == "ru"
                        else "Javobingiz foydalanuvchiga yuborildi.")


# Обработка ответа пользователя на запрос «У вас есть ещё вопросы?»
@dp.message(lambda message: message.text in ["Да", "Ha", "Нет", "Yo'q"])
async def followup_handler(message: Message):
    user_id = message.from_user.id

    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    language = result[0] if result else "ru"

    if message.text in ["Да", "Ha"]:
        # Если пользователь ответил "Да"
        text = ("Хорошо, вы можете задать вопрос, нажав кнопку 'Вопрос к администратору'."
                if language == "ru"
                else "Yaxshi, siz 'Adminstratorga savol' tugmasini bosib savol bera olasiz.")
        await message.answer(text, reply_markup=main_menu[language])
    else:
        # Если ответ "Нет" – предлагаем оценить бота
        text = (
            "Хорошо, тогда оцените A'lochi bot." if language == "ru"
            else "Yaxshi, unday bo'lsa A'lochi botni baholang.")
        await message.answer(text, reply_markup=rating_keyboard[language])


# Обработка оценки (нажатие кнопок с 1-5 звёздами)
@dp.message(lambda message: message.text in ["1 ⭐", "2 ⭐", "3 ⭐", "4 ⭐", "5 ⭐"])
async def rating_handler(message: Message):
    user_id = message.from_user.id

    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    language = result[0] if result else "ru"

    thank_text = "Спасибо за оценку!" if language == "ru" else "Baholaganingiz uchun, raxmat!"
    await message.answer(thank_text, reply_markup=main_menu[language])


# Команда "Мои данные"
@dp.message(lambda message: message.text in ["Мои данные", "Mening ma'lumotlarim"])
async def my_data(message: Message):
    user_id = message.from_user.id

    # Получаем данные пользователя из базы данных, включая номер телефона
    cursor.execute("SELECT fullname, age, language, phone FROM user WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()

    if user_data:
        fullname, age, language, phone = user_data

        # Формируем сообщение в зависимости от языка пользователя
        if language == "ru":
            response = f"Ваши данные:\nИмя: {fullname}\nКласс: {age}\nТелефон: {phone}"
        else:  # Для узбекского языка
            response = f"Sizning ma'lumotlaringiz:\nIsmingiz: {fullname}\nSinf: {age}\nTelefon: {phone}"

        await message.answer(response, reply_markup=main_menu[language])
    else:
        # Если данных пользователя нет, можно задать язык по умолчанию (например, 'ru')
        default_language = "ru"
        await message.answer(
            "Вы еще не зарегистрированы. Пожалуйста, сначала введите ваши данные."
            if default_language == "ru"
            else "Siz hali ro'yxatdan o'tmagansiz. Iltimos, avval ma'lumotlaringizni kiriting.",
            reply_markup=main_menu[default_language]
        )


# Меню администратора: Список пользователей
@dp.message(lambda message: message.from_user.id == ADMIN_ID and message.text == "Список пользователей")
async def list_users(message: Message):
    cursor.execute("SELECT user_id, fullname, age, language FROM user")
    users = cursor.fetchall()

    if users:
        user_list = "\n".join([f"ID: {user[0]}, Имя: {user[1]}, Класс: {user[2]}" for user in users])
        language = users[0][3]  # Получаем язык первого пользователя

        await message.answer(
            f"Список пользователей:\n{user_list}" if language == "ru"
            else f"Foydalanuvchilar ro'yxati:\n{user_list}"
        )
    else:
        language = users[0][3]  # Получаем язык первого пользователя
        await message.answer(
            "Нет пользователей в базе данных." if language == "ru"
            else "Ma'lumotlar bazasida foydalanuvchilar yo'q."
        )


# Обработка команды "Список пользователей" для администратора
@dp.message(lambda message: message.from_user.id == ADMIN_ID and message.text == "Список пользователей")
async def list_users(message: Message):
    user_id = message.from_user.id

    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    language = cursor.fetchone()[0]

    cursor.execute("SELECT user_id, fullname, age FROM user")
    users = cursor.fetchall()

    if users:
        user_list = "\n".join([f"ID: {user[0]}, Имя: {user[1]}, Класс: {user[2]}" for user in users])
        await message.answer(
            f"Список пользователей:\n{user_list}" if language == "ru" else f"Foydalanuvchilar ro'yxati:\n{user_list}",
            reply_markup=admin_menu[language])
    else:
        await message.answer(
            "Нет пользователей в базе данных." if language == "ru" else "Ma'lumotlar bazasida foydalanuvchilar yo'q.",
            reply_markup=admin_menu[language])


# Код для обработки нажатия кнопки "Настройки" или "Sozlamalar"
@dp.message(lambda message: message.text in ["Настройки", "Sozlamalar"])
async def settings_handler(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    language = cursor.fetchone()[0]  # Получаем язык пользователя из базы данных

    await message.answer(
        "Выберите действие:" if language == "ru" else "Buyruqni tanlang:",
        reply_markup=settings_menu[language]
    )


# Обработка изменения языка
@dp.message(lambda message: message.text in ["Изменить язык", "Tilni o'zgartirish"])
async def change_language(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    language = cursor.fetchone()[0]

    lang_selection = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="O'zbekcha", callback_data="lang_uz")]
    ])

    await message.answer(
        "Выберите язык:" if language == "ru" else "Tilni tanlang:",
        reply_markup=lang_selection
    )


# Обработка возврата в главное меню
@dp.message(lambda message: message.text in ["Назад", "Orqaga"])
async def back_to_main_menu(message: Message):
    user_id = message.from_user.id
    cursor.execute("SELECT language FROM user WHERE user_id = ?", (user_id,))
    language = cursor.fetchone()[0]  # Получаем язык пользователя

    await message.answer(
        "Главное меню:" if language == "ru" else "Asiya menyu:",
        reply_markup=main_menu[language]  # Отправляем основное меню
    )


# Обработчик команды «Добавить тесты / Testlarni qo'shish» для администратора
@dp.message(
    lambda message: message.from_user.id == ADMIN_ID and message.text in ["Добавить тесты", "Testlarni qo'shish"])
async def add_tests_start(message: Message, state: FSMContext):
    print("[DEBUG] Команда 'Добавить тесты' принята")  # Логируем событие
    await state.clear()
    await state.set_state(AdminTestCreationStates.choosing_subject)
    print(f"[DEBUG] Состояние установлено: {await state.get_state()}")  # Логируем состояние

    language = get_user_language(message.from_user.id)
    text_ru = "Выберите предмет, по которому вы хотите добавить тесты:"
    text_uz = "Qaysi fan bo‘yicha test qo‘shmoqchi ekanligingizni tanlang:"

    kb = subject_keyboard.get(language, subject_keyboard["ru"])
    await message.answer(text_ru if language == "ru" else text_uz, reply_markup=kb)


@dp.message()
async def check_state_debug(message: Message, state: FSMContext):
    current_state = await state.get_state()
    print(f"[DEBUG] Текущее состояние перед обработкой: {current_state}")


# Обработка выбора предмета
@dp.message(AdminTestCreationStates.choosing_subject)
async def process_test_subject(message: Message, state: FSMContext):
    print(f"[DEBUG] Вызван process_test_subject. Состояние: {await state.get_state()}")

    subject = message.text
    await state.update_data(subject=subject)
    await state.set_state(AdminTestCreationStates.choosing_class)

    print(f"[DEBUG] Предмет выбран: {subject}")
    print(f"[DEBUG] Новое состояние: {await state.get_state()}")

    language = get_user_language(message.from_user.id)
    text_ru = "Теперь введите класс, для которого вы хотите добавить тесты:"
    text_uz = "Endi qaysi sinf uchun test qo‘shmoqchi ekanligingizni kiriting:"

    kb = class_keyboard.get(language, class_keyboard["ru"])
    await message.answer(text_ru if language == "ru" else text_uz, reply_markup=kb)


# Обработка выбора класса
@dp.message(AdminTestCreationStates.choosing_class)
async def process_test_class(message: Message, state: FSMContext):
    language = get_user_language(message.from_user.id)
    valid_classes = ["1 класс", "2 класс", "3 класс", "4 класс", "5 класс", "6 класс",
                     "7 класс", "8 класс", "9 класс", "10 класс", "11 класс",
                     "1-sinf", "2-sinf", "3-sinf", "4-sinf", "5-sinf", "6-sinf",
                     "7-sinf", "8-sinf", "9-sinf", "10-sinf", "11-sinf"]

    print(f"[LOG] Получен класс: {message.text}")  # Лог

    if message.text not in valid_classes:
        await message.answer("❌ Пожалуйста, выберите класс, нажав на кнопку.")
        return

    test_class = message.text
    await state.update_data(test_class=test_class, question_count=0)
    await state.set_state(AdminTestCreationStates.waiting_for_question)

    text_ru = "Введите вопрос:"
    text_uz = "Savolni kiriting:"

    print(f"[LOG] Переключение на waiting_for_question")  # Лог
    await message.answer(text_ru if language == "ru" else text_uz, reply_markup=ReplyKeyboardRemove())


# Обработка ввода текста вопроса
@dp.message(AdminTestCreationStates.waiting_for_question)
async def process_test_question(message: Message, state: FSMContext):
    language = get_user_language(message.from_user.id)
    question_text = message.text
    await state.update_data(question_text=question_text)
    await state.set_state(AdminTestCreationStates.waiting_for_correct_answer)
    text_ru = "Введите правильный ответ:"
    text_uz = "To‘g‘ri javobni kiriting:"
    await message.answer(text_ru if language == "ru" else text_uz)


# Обработка ввода правильного ответа
@dp.message(AdminTestCreationStates.waiting_for_correct_answer)
async def process_test_correct(message: Message, state: FSMContext):
    language = get_user_language(message.from_user.id)
    correct_answer = message.text
    await state.update_data(correct_answer=correct_answer)
    await state.set_state(AdminTestCreationStates.waiting_for_incorrect_answers)
    text_ru = "Введите неправильные ответы, разделенные запятой:"
    text_uz = "Noto‘g‘ri javoblarni vergul bilan ajratib kiriting:"
    await message.answer(text_ru if language == "ru" else text_uz)


# Обработка ввода неправильных ответов и сохранение вопроса
@dp.message(AdminTestCreationStates.waiting_for_incorrect_answers)
async def process_test_incorrect(message: Message, state: FSMContext):
    language = get_user_language(message.from_user.id)
    incorrect_answers = message.text  # Ожидается список неправильных ответов через запятую
    data = await state.get_data()
    subject = data.get("subject")
    test_class = data.get("test_class")
    question_text = data.get("question_text")
    correct_answer = data.get("correct_answer")
    question_count = data.get("question_count", 0) + 1

    # Формируем строку с ответами: правильный и неправильные разделяем, например, точкой с запятой
    answers = correct_answer + ";" + incorrect_answers

    # Сохраняем вопрос в таблицу tests (здесь предполагается, что для русского языка поле questions_ru)
    cursor.execute(
        "INSERT INTO tests (subject, class, questions_ru, answers) VALUES (?, ?, ?, ?)",
        (subject, test_class, question_text, answers)
    )
    conn.commit()

    # Если количество вопросов достигло 15, завершаем набор
    if question_count >= 15:
        text_ru = "Тесты достигли максимального количества."
        text_uz = "Testlar maksimal soniga yetdi."
        await message.answer(text_ru if language == "ru" else text_uz, reply_markup=admin_menu[language])
        await state.clear()
    else:
        # Обновляем счетчик вопросов
        await state.update_data(question_count=question_count)
        # Клавиатура для завершения добавления тестов вручную
        finish_kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Завершить добавление тестов")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        text_ru = "Хорошо, теперь отправьте следующий вопрос или нажмите 'Завершить добавление тестов'."
        text_uz = "Yaxshi, endi keyingi savolni kiriting yoki 'Test qo‘shishni tugatish' tugmasini bosing."
        await state.set_state(AdminTestCreationStates.waiting_for_question)
        await message.answer(text_ru if language == "ru" else text_uz, reply_markup=finish_kb)


# Обработка нажатия кнопки «Завершить добавление тестов»
@dp.message(lambda message: message.text in ["Завершить добавление тестов", "Test qo‘shishni tugatish"] and
                            message.from_user.id == ADMIN_ID)
async def finish_test_adding(message: Message, state: FSMContext):
    language = get_user_language(message.from_user.id)
    text_ru = "Добавление тестов завершено."
    text_uz = "Test qo‘shish tugatildi."
    await message.answer(text_ru if language == "ru" else text_uz, reply_markup=admin_menu[language])
    await state.clear()


@dp.message()
async def debug_all_messages(message: Message):
    print(f"[DEBUG] Получено сообщение: {message.text}")


@dp.message()
async def debug_messages(message: Message, state: FSMContext):
    current_state = await state.get_state()
    print(f"[DEBUG] Получено сообщение: {message.text}, Текущее состояние: {current_state}")


# Запуск бота
if __name__ == "__main__":
    import asyncio

    logging.info("Бот запущен и готов к работе.")
    asyncio.run(dp.start_polling(bot))
