import asyncio
import random
import sqlite3

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

from deep_translator import GoogleTranslator

TOKEN = "8631132859:AAHrUOeXbUwnMDpyA0gz8OLQg7n_O-zZtew"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# БАЗА
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

# СОСТОЯНИЕ
user_state = {}

# МЕНЮ
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📖 Словарь"), KeyboardButton(text="📚 Выученные")],
        [KeyboardButton(text="➕ Добавить"), KeyboardButton(text="🎯 Тренировка")]
    ],
    resize_keyboard=True
)

training_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧩 Выбери перевод")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

mode_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="EN → RU")],
        [KeyboardButton(text="RU → EN")],
        [KeyboardButton(text="MIX")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

# ПЕРЕВОД
def translate_word(word):
    try:
        if any("а" <= c.lower() <= "я" for c in word):
            ru = word
            en = GoogleTranslator(source='ru', target='en').translate(word)
        else:
            en = word
            ru = GoogleTranslator(source='en', target='ru').translate(word)

        return en.capitalize(), ru.capitalize()
    except:
        return word.capitalize(), "Ошибка"

# КВИЗ
def get_quiz(user_id, mode):
    cursor.execute("SELECT word, translation FROM words WHERE user_id=?", (user_id,))
    words = cursor.fetchall()

    if len(words) < 4:
        return None, None, None

    correct = random.choice(words)

    if mode == "EN → RU":
        question = correct[0]
        correct_answer = correct[1]
        options = [w[1] for w in random.sample(words, 4)]

    elif mode == "RU → EN":
        question = correct[1]
        correct_answer = correct[0]
        options = [w[0] for w in random.sample(words, 4)]

    else:
        return get_quiz(user_id, random.choice(["EN → RU", "RU → EN"]))

    if correct_answer not in options:
        options[0] = correct_answer

    random.shuffle(options)
    return question, correct_answer, options

def build_quiz_keyboard(options):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=options[0]), KeyboardButton(text=options[1])],
            [KeyboardButton(text=options[2]), KeyboardButton(text=options[3])],
            [KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )

# СТАРТ
@dp.message(Command("start"))
async def start(message: types.Message):
    user_state[message.from_user.id] = "menu"
    await message.answer("Главное меню 👇", reply_markup=main_menu)

# ОСНОВНОЙ ХЕНДЛЕР
@dp.message()
async def handler(message: types.Message):
    text = message.text
    user_id = message.from_user.id
    state = user_state.get(user_id, "menu")

    if text.startswith("/"):
        return

    # НАЗАД
    if text == "⬅️ Назад":
        user_state[user_id] = "menu"
        await message.answer("Главное меню 👇", reply_markup=main_menu)
        return

    # СЛОВАРЬ
    if text == "📖 Словарь":
        cursor.execute("SELECT word, translation FROM words WHERE user_id=? AND status='learning'", (user_id,))
        words = cursor.fetchall()

        if not words:
            await message.answer("Словарь пуст 😢", reply_markup=main_menu)
            return

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"{w} — {t}", callback_data=f"word:{w}:{t}")]
            for w, t in words
        ])

        await message.answer("📖 Твои слова:", reply_markup=keyboard)
        return

    # ВЫУЧЕННЫЕ
    if text == "📚 Выученные":
        cursor.execute("SELECT word, translation FROM words WHERE user_id=? AND status='learned'", (user_id,))
        words = cursor.fetchall()

        if not words:
            await message.answer("Нет выученных слов 😢", reply_markup=main_menu)
            return

        text_out = "\n".join([f"{w} — {t}" for w, t in words])
        await message.answer(f"📚 Выученные ({len(words)} слов):\n\n{text_out}", reply_markup=main_menu)
        return

    # ДОБАВИТЬ
    if text == "➕ Добавить":
        user_state[user_id] = "adding"
        await message.answer("Напиши слово ✍️")
        return

    # ТРЕНИРОВКА
    if text == "🎯 Тренировка":
        await message.answer("Выбери тренировку:", reply_markup=training_menu)
        return

    if text == "🧩 Выбери перевод":
        await message.answer("Выбери режим:", reply_markup=mode_menu)
        return

    if text in ["EN → RU", "RU → EN", "MIX"]:
        user_state[user_id] = {"mode": text}
        await send_quiz(message, user_id)
        return

    # КВИЗ ОТВЕТ
    if isinstance(user_state.get(user_id), dict):
        correct = user_state[user_id]["answer"]

        if text == correct:
            await message.answer("🔥 Правильно!")
        else:
            await message.answer(f"❌ Неправильно\nПравильный ответ: {correct}")

        await send_quiz(message, user_id)
        return

    # ДОБАВЛЕНИЕ
    if state == "adding":
        en, ru = translate_word(text)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить в словарь", callback_data=f"add:{en}:{ru}")]
        ])

        await message.answer(f"{en} — {ru}", reply_markup=keyboard)
        return

    # ОБЫЧНЫЙ ПЕРЕВОД
    en, ru = translate_word(text)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить в словарь", callback_data=f"add:{en}:{ru}")]
    ])
    await message.answer(f"{en} — {ru}", reply_markup=keyboard)

# CALLBACK
@dp.callback_query()
async def callbacks(callback: types.CallbackQuery):
    await callback.answer()
    data = callback.data
    user_id = callback.from_user.id

    # ДОБАВИТЬ
    if data.startswith("add"):
        _, word, translation = data.split(":")

        cursor.execute(
            "SELECT * FROM words WHERE user_id=? AND word=?",
            (user_id, word)
        )
        if cursor.fetchone():
            await callback.message.answer("Уже есть в словаре ⚠️")
            return

        cursor.execute(
            "INSERT INTO words (user_id, word, translation, status) VALUES (?, ?, ?, ?)",
            (user_id, word, translation, "learning")
        )
        conn.commit()

        await callback.message.answer(f"Добавлено: {word} — {translation} 📚")

    # ОТКРЫТЬ СЛОВО
    elif data.startswith("word"):
        _, word, translation = data.split(":")

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Выучил", callback_data=f"learn:{word}")],
            [InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete:{word}")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
        ])

        await callback.message.answer(f"{word} — {translation}", reply_markup=keyboard)

    # ВЫУЧИЛ
    elif data.startswith("learn"):
        _, word = data.split(":")

        cursor.execute(
            "UPDATE words SET status='learned' WHERE user_id=? AND word=?",
            (user_id, word)
        )
        conn.commit()

        await callback.message.answer("Перенесено в выученные ✅")

    # УДАЛИТЬ
    elif data.startswith("delete"):
        _, word = data.split(":")

        cursor.execute(
            "DELETE FROM words WHERE user_id=? AND word=?",
            (user_id, word)
        )
        conn.commit()

        await callback.message.answer("Удалено ❌")

    elif data == "back":
        await callback.message.answer("Главное меню 👇", reply_markup=main_menu)

async def send_quiz(message, user_id):
    mode = user_state[user_id]["mode"]

    question, correct, options = get_quiz(user_id, mode)

    if not question:
        await message.answer("Добавь минимум 4 слова 😢")
        return

    user_state[user_id]["answer"] = correct

    keyboard = build_quiz_keyboard(options)
    await message.answer(f"👉 {question}", reply_markup=keyboard)

import threading
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running')

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), Handler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# ЗАПУСК
async def main():
    await dp.start_polling(bot)

asyncio.run(main())