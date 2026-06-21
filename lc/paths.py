from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_FILE = ROOT / "problems" / "hot100.json"
WORKSPACE = ROOT / "workspace"
DATA = ROOT / "data"
PROGRESS_FILE = DATA / "progress.json"
