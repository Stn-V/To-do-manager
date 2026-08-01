import os
import json
from model.task import Task


class Storage:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._ensure_exists()

    def _ensure_exists(self):
        # создаём директорию, если её нет
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

        # создаём файл, если его нет
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump([], f)

    def load(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except json.JSONDecodeError:
            # файл повреждён → восстанавливаем
            raw = []
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump([], f)

        return [Task.from_dict(item) for item in raw]

    def save(self, tasks):
        serializable = [t.to_dict() for t in tasks]

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(serializable, f, ensure_ascii=False, indent=2)

