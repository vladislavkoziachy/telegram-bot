import asyncio
from deep_translator import GoogleTranslator
import re

def is_russian(text: str) -> bool:
    # Простая проверка на наличие кириллицы
    return bool(re.search('[а-яА-Я]', text))

async def translate_text(text: str) -> dict:
    """
    Определяет язык и переводит (RU <-> EN).
    Возвращает словарь с оригиналом и переводом.
    Асинхронная обертка для предотвращения блокировки бота.
    """
    if is_russian(text):
        source, target = 'ru', 'en'
    else:
        source, target = 'en', 'ru'
    
    try:
        # Запускаем синхронный перевод в отдельном потоке
        translator = GoogleTranslator(source=source, target=target)
        translation = await asyncio.to_thread(translator.translate, text)
        
        return {
            "original": text,
            "translated": translation,
            "source_lang": source
        }
    except Exception as e:
        print(f"Ошибка перевода: {e}")
        return None
