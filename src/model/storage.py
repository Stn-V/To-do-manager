import json
import os
from  typing import List
from model.task import Task
class Storage:
    def __init__(self, filepath:str):
        self.filepath = filepath
        self.exist()
        
    def exist(self):
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                json.dump([], f, indent=4)

    def load(self) -> List[Task]:
        try:
            with open(self.filepath, "r") as f:
                data = json.load(f)
            if not isinstance(data, list):
                return []
            return [Task.from_dict(item) for item in data]
        except (json.JSONDecodeError, FileNotFoundError):
            with open(self.filepath, "w") as f:
                json.dump([], f, indent=4)
            return []



    def save(self, tasks: List[Task]):
        data = [task.to_dict() for task in tasks]
        with open(self.filepath, "w") as f:
            json.dump(data, f, indent=4)