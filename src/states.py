from aiogram.fsm.state import StatesGroup, State

class AddingWordStates(StatesGroup):
    waiting_for_word = State()

class TrainingStates(StatesGroup):
    waiting_for_source = State()
    waiting_for_direction = State()
    waiting_for_answer = State()

class TranslatorStates(StatesGroup):
    waiting_for_text = State()

class LanguageStates(StatesGroup):
    waiting_for_interface_lang = State()
    waiting_for_learning_lang = State()
