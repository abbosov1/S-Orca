from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

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
