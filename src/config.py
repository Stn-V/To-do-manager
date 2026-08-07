import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
TASKS_FILE = DATA_DIR / "tasks.json"
RECURRING_TASKS_FILE = DATA_DIR / "recurring_tasks.json"

DEADLINE_CHECK_INTERVAL_MS = 60 * 1000
DEADLINE_WINDOW_MINUTES = 30