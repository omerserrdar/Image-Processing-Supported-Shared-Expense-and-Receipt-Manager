"""
TR: Çoklu dil (i18n) yardımcı modülü.
EN: Internationalization (i18n) helper module.
"""

from i18n import en, tr

# TR: Dil kodu -> ceviri sozlugu haritasi
# EN: Language code -> translation dictionary mapping

_LANGUAGES = {
    "en": en.translations,
    "tr": tr.translations,
}


def t(key: str, lang: str = "en") -> str:
    """
    TR: Verilen anahtarın çevirisini döndürür. Bulamazsa anahtarı döndürür.
    EN: Returns the translation for the given key. Returns the key itself if not found.
    """
    # TR: Dil yoksa EN'e fallback yap
    # EN: Fallback to EN if language is missing
    return _LANGUAGES.get(lang, _LANGUAGES["en"]).get(key, key)


def get_available_languages() -> list[dict]:
    """
    TR: Kullanılabilir dilleri döndürür.
    EN: Returns available languages.
    """
    # TR: UI'da gosterilecek dil listesi
    # EN: Language list shown in the UI
    return [
        {"code": "en", "name": "English", "flag": "🇬🇧"},
        {"code": "tr", "name": "Türkçe", "flag": "🇹🇷"},
    ]
