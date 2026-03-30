from deep_translator import GoogleTranslator

FLAGS = {
    "en": "🇬🇧",
    "ru": "🇷🇺",
    "uk": "🇺🇦",
    "pl": "🇵🇱",
    "es": "🇪🇸"
}

def translate_word(word: str, user_lang: str, learn_lang: str) -> tuple[str, str]:
    """Returns (word_in_learning_lang, word_in_interface_lang)"""
    try:
        # We translate the input to BOTH learning language and interface language.
        # This completely avoids guessing the source language via alphabets.
        word_learn = GoogleTranslator(source='auto', target=learn_lang).translate(word)
        word_native = GoogleTranslator(source='auto', target=user_lang).translate(word)
        
        return word_learn.capitalize(), word_native.capitalize()
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
