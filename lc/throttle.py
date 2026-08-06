import datetime
import json
import os

from .paths import DATA, PROGRESS_FILE
from .config import TEST_COOLDOWN_SECONDS, LOCK_TIMEOUT_SECONDS

LOCK_FILE = DATA / ".test_lock"


def _now():
    return datetime.datetime.now()


def acquire_lock():
    """Try to acquire the test lock. Returns True if acquired, False if held by another process."""
    DATA.mkdir(exist_ok=True)
    if LOCK_FILE.exists():
        try:
            info = json.loads(LOCK_FILE.read_text(encoding="utf-8"))
            created = datetime.datetime.fromisoformat(info["at"])
            if (_now() - created).total_seconds() < LOCK_TIMEOUT_SECONDS:
                return False
        except (json.JSONDecodeError, KeyError, ValueError, OSError):
            pass
    LOCK_FILE.write_text(
        json.dumps({"pid": os.getpid(), "at": _now().isoformat(timespec="seconds")}),
        encoding="utf-8",
    )
    return True


def release_lock():
    """Release the test lock."""
    try:
        LOCK_FILE.unlink()
    except OSError:
        pass


def check_cooldown(problem_id):
    """Check if enough time has passed since the last test for this problem.

    Returns (can_run, remaining_seconds).
    """
    if not PROGRESS_FILE.exists():
        return True, 0
    try:
        progress = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return True, 0
    last_timestamp = progress.get("last_test", {}).get(str(problem_id))
    if not last_timestamp:
        return True, 0
    try:
        last = datetime.datetime.fromisoformat(last_timestamp)
    except ValueError:
        return True, 0
    elapsed = (_now() - last).total_seconds()
    remaining = TEST_COOLDOWN_SECONDS - elapsed
    if remaining <= 0:
        return True, 0
    return False, remaining


def record_test_time(problem_id):
    """Record the timestamp of the last test for a problem."""
    DATA.mkdir(exist_ok=True)
    try:
        progress = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        progress = {"done": {}}
    progress.setdefault("last_test", {})[str(problem_id)] = _now().isoformat(timespec="seconds")
    with PROGRESS_FILE.open("w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)
