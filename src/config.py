from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TASKS_FILE = DATA_DIR / "tasks.json"
RECURRING_TASKS_FILE = DATA_DIR / "recurring_tasks.json"

DEADLINE_CHECK_INTERVAL_MS = 5 * 60 * 1000  # 5 MINUTES
DEADLINE_WINDOW_MINUTES = 30