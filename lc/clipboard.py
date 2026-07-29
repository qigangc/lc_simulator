import subprocess
import sys


def copy_to_clipboard(text):
    """Copy text to the system clipboard. Returns True on success."""
    if sys.platform == "win32":
        cmd = ["clip"]
    elif sys.platform == "darwin":
        cmd = ["pbcopy"]
    else:
        cmd = ["xclip", "-selection", "clipboard"]

    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        proc.communicate(input=text.encode("utf-8"))
        return proc.returncode == 0
    except (OSError, FileNotFoundError):
        if sys.platform != "win32" and sys.platform != "darwin":
            try:
                proc = subprocess.Popen(
                    ["xsel", "--clipboard", "--input"], stdin=subprocess.PIPE
                )
                proc.communicate(input=text.encode("utf-8"))
                return proc.returncode == 0
            except (OSError, FileNotFoundError):
                return False
        return False
