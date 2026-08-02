"""Simple colored output using colorama.

Respects the user's theme setting: 'dark' uses full color, 'light' strips
color for readability on bright terminal backgrounds.
"""
import colorama

colorama.init(autoreset=True)


def _use_color():
    try:
        from .settings import load_settings
        return load_settings().get("theme", "dark") == "dark"
    except Exception:
        return True


def red(text):
    if not _use_color():
        return text
    return f"{colorama.Fore.RED}{text}{colorama.Style.RESET_ALL}"


def green(text):
    if not _use_color():
        return text
    return f"{colorama.Fore.GREEN}{text}{colorama.Style.RESET_ALL}"


def yellow(text):
    if not _use_color():
        return text
    return f"{colorama.Fore.YELLOW}{text}{colorama.Style.RESET_ALL}"


def cyan(text):
    if not _use_color():
        return text
    return f"{colorama.Fore.CYAN}{text}{colorama.Style.RESET_ALL}"


def bold(text):
    if not _use_color():
        return text
    return f"{colorama.Style.BRIGHT}{text}{colorama.Style.RESET_ALL}"