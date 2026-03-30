from deep_translator import GoogleTranslator

def translate_word(word: str, target_lang: str = 'en') -> tuple[str, str]:
    """Returns (en_word, ru_word) or (word, translation) depending on learning language"""
    try:
        # Simple detection: if contains cyrillic, it's likely the native language (RU/UK)
        # We want to translate TO the learning language (target_lang)
        if any("\u0400" <= c <= "\u04FF" or c.lower() == 'ё' for c in word):
            source = 'auto'
            target = target_lang
            translated = GoogleTranslator(source=source, target=target).translate(word)
            return translated.capitalize(), word.capitalize()
        else:
            # If not cyrillic, it's likely the learning language or something else
            # We translate TO 'ru' (or user's interface lang, but for now 'ru' as a bridge is common)
            # Better: translate to 'ru' if it's the interface lang. 
            # For simplicity, we assume if it's not native, it's the learning language.
            source = target_lang
            target = 'ru'
            translated = GoogleTranslator(source=source, target=target).translate(word)
            return word.capitalize(), translated.capitalize()

    except Exception:
        return word.capitalize(), "Error"

def translate_full_text(text: str, target_lang: str = 'ru') -> str:
    """Translates text to the specified target language using auto-detection."""
    try:
        # If we want a smart toggle: if text is in RU/UK, translate to EN/PL/ES
        # If text is in EN/PL/ES, translate to RU/UK
        # For now, let's keep it simple: translate TO target_lang with auto-detection
        return GoogleTranslator(source='auto', target=target_lang).translate(text)
    except Exception:
        return "⚠️ Error."
