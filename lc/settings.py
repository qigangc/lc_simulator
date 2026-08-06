"""User settings: theme and font size preferences."""

import json

from .paths import DATA

SETTINGS_FILE = DATA / "settings.json"

DEFAULT_SETTINGS = {
    "theme": "dark",
    "font_size": 16,
}

VALID_THEMES = ("dark", "light")
VALID_FONT_SIZES = (14, 16, 18)


def load_settings():
    if not SETTINGS_FILE.exists():
        return dict(DEFAULT_SETTINGS)
    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as f:
            file_data = json.load(f)
        settings = dict(DEFAULT_SETTINGS)
        settings.update(file_data)
        return settings
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    DATA.mkdir(exist_ok=True)
    with SETTINGS_FILE.open("w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def update_setting(key, value):
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
    return settings
