# lang.py

LANGUAGES = {
    "en": {
        "menu_skeleton": "Skeleton Anatomy",
        "menu_muscle": "Muscle Anatomy",
        "menu_settings": "Settings",
        "menu_quit": "Quit",
        "viewer_closed": "Viewer closed, returning to main menu.",
    },
    "hu": {
        "menu_skeleton": "Csont Anatómia",
        "menu_muscle": "Izom Anatómia",
        "menu_settings": "Beállítások",
        "menu_quit": "Kilépés",
        "viewer_closed": "Nézet bezárva, visszatérés a főmenübe.",
    }
}

# Default language
current_lang = "en"


def set_language(lang_code):
    global current_lang
    if lang_code in LANGUAGES:
        current_lang = lang_code
    else:
        print(f"Language {lang_code} not available.")


def t(key):
    """Return the translated text for current language"""
    return LANGUAGES[current_lang].get(key, key)
