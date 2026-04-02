from aiogram.fsm.state import StatesGroup, State

class AddWord(StatesGroup):
    waiting_for_word = State()          # Ожидание ввода самого слова
    waiting_for_translation = State()   # Ожидание ввода перевода

class Training(StatesGroup):
    choosing_type = State()         # Выбор типа (например, "Выбери перевод")
    choosing_pool = State()         # Выбор папки (Словарь или Выученные)
    choosing_direction = State()    # Выбор направления (RU-EN, EN-RU, Mix)
    waiting_for_answer = State()    # Ожидание ввода ответа в квизе
