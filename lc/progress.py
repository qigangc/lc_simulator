import json
import datetime
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
    progress.setdefault("done", {})[str(problem_id)] = {"at": datetime.datetime.now().isoformat(timespec="seconds")}
    save_progress(progress)


def start_problem(problem_id):
    """Record the start time for a problem."""
    progress = load_progress()
    progress.setdefault("started", {})[str(problem_id)] = datetime.datetime.now().isoformat(timespec="seconds")
    save_progress(progress)


def elapsed_time(problem_id):
    """Return human-readable elapsed time for a problem since started_at.
    Returns None if no start time recorded."""
    progress = load_progress()
    started_str = progress.get("started", {}).get(str(problem_id))
    if not started_str:
        return None
    started = datetime.datetime.fromisoformat(started_str)
    elapsed = datetime.datetime.now() - started
    return _format_duration(elapsed)


def total_elapsed_time():
    """Return total elapsed time across all completed problems that have start records."""
    progress = load_progress()
    total = 0
    for pid, info in progress.get("done", {}).items():
        started_str = progress.get("started", {}).get(pid)
        if started_str:
            started = datetime.datetime.fromisoformat(started_str)
            done_at = datetime.datetime.fromisoformat(info["at"])
            total += (done_at - started).total_seconds()
    return _format_duration(datetime.timedelta(seconds=int(total))) if total > 0 else "0s"


def _format_duration(td):
    """Format a timedelta into a human-readable string like '12m 34s' or '1h 23m'."""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    if minutes > 0:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"
