"""Simple colored output using colorama."""
import colorama

colorama.init(autoreset=True)


def red(text):
    return f"{colorama.Fore.RED}{text}{colorama.Style.RESET_ALL}"


def green(text):
    return f"{colorama.Fore.GREEN}{text}{colorama.Style.RESET_ALL}"


def yellow(text):
    return f"{colorama.Fore.YELLOW}{text}{colorama.Style.RESET_ALL}"


def cyan(text):
    return f"{colorama.Fore.CYAN}{text}{colorama.Style.RESET_ALL}"


def bold(text):
    return f"{colorama.Style.BRIGHT}{text}{colorama.Style.RESET_ALL}"