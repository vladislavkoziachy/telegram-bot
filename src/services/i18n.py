import json
import os

class I18n:
    def __init__(self, locales_path: str):
        self.locales_path = locales_path
        self.translations = {}
        self.load_translations()

    def load_translations(self):
        for filename in os.listdir(self.locales_path):
            if filename.endswith(".json"):
                lang = filename.split(".")[0]
                with open(os.path.join(self.locales_path, filename), "r", encoding="utf-8") as f:
                    self.translations[lang] = json.load(f)

    def get_text(self, key: str, lang: str, **kwargs) -> str:
        lang_data = self.translations.get(lang, self.translations.get("ru", {}))
        text = lang_data.get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except KeyError:
                return text
        return text

    def get_all_translations(self, key: str) -> list[str]:
        res = set()
        for d in self.translations.values():
            val = d.get(key)
            if val:
                res.add(val)
        return list(res) if res else [key]

# Global instance
i18n = I18n(os.path.join(os.path.dirname(__file__), "..", "locales"))

def _(key: str, lang: str = "ru", **kwargs) -> str:
    return i18n.get_text(key, lang, **kwargs)

def get_all_translated(key: str) -> list[str]:
    return i18n.get_all_translations(key)
