import json
from datetime import datetime
from .paths import DATA, PROGRESS_FILE


def load_progress():
    if not PROGRESS_FILE.exists():
        return {"done": {}}
    try:
        with PROGRESS_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"done": {}}


def save_progress(progress):
    DATA.mkdir(exist_ok=True)
    with PROGRESS_FILE.open("w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def is_done(problem_id):
    return str(problem_id) in load_progress().get("done", {})


def mark_done(problem_id):
    progress = load_progress()
    progress.setdefault("done", {})[str(problem_id)] = {"at": datetime.now().isoformat(timespec="seconds")}
    save_progress(progress)
