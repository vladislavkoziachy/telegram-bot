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
    pass # Deleting this since we don't use it anymore but keeping class to avoid imports breaking if any found elsewhere (unlikely)
