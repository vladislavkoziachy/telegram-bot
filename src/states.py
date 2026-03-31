from aiogram.fsm.state import StatesGroup, State

class AddWord(StatesGroup):
    waiting_for_word = State()          # Ожидание ввода самого слова
    waiting_for_translation = State()   # Ожидание ввода перевода
