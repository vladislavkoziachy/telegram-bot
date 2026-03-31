from deep_translator import GoogleTranslator

def translate_word(word: str) -> tuple[str, str]:
    """Returns (en_word, ru_word)"""
    try:
        # Simple detection: if contains cyrillic, it's likely the native language (RU)
        if any("\u0400" <= c <= "\u04FF" or c.lower() == 'ё' for c in word):
            word_learn = GoogleTranslator(source='auto', target='en').translate(word)
            word_native = word
        else:
            word_learn = word
            word_native = GoogleTranslator(source='auto', target='ru').translate(word)
        
        return word_learn.capitalize(), word_native.capitalize()
    except Exception:
        return word.capitalize(), "ошибка"

def translate_full_text(text: str, target_lang: str = 'ru') -> str:
    """Translates text to the specified target language using auto-detection."""
    try:
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception:
        return "⚠️ Ошибка."
