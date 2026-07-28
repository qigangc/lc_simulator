import os
import subprocess
import sys

from .paths import NOTES_DIR
from .problems import note_filename


def note_path(problem):
    return NOTES_DIR / note_filename(problem)


def render_note_template(problem):
    title = problem.get("title_en", problem.get("slug", ""))
    return (
        f"# {problem['id']}. {title}\n"
        f"\n"
        f"## {('思路' if os.environ.get('LC_LANG') == 'zh' else 'Approach')}\n"
        f"\n"
        f"- \n"
        f"\n"
        f"## {('伪代码' if os.environ.get('LC_LANG') == 'zh' else 'Pseudocode')}\n"
        f"\n"
        f"```\n"
        f"\n"
        f"```\n"
        f"\n"
        f"## {('复杂度' if os.environ.get('LC_LANG') == 'zh' else 'Complexity')}\n"
        f"\n"
        f"- Time: \n"
        f"- Space: \n"
    )


def ensure_note(problem):
    NOTES_DIR.mkdir(exist_ok=True)
    path = note_path(problem)
    if not path.exists():
        path.write_text(render_note_template(problem), encoding="utf-8")
    return path


def read_note(problem):
    path = note_path(problem)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def open_note(problem):
    path = ensure_note(problem)
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL")
    if not editor:
        editor = "notepad" if sys.platform == "win32" else "vi"
    subprocess.call([editor, str(path)])
    return path
