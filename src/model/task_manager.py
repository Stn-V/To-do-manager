from datetime import datetime, timedelta
from typing import Optional, List
from model.task import Task, Status
from model.storage import Storage
class TaskManager:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.tasks: List[Task] = self.storage.load()
        self.next_id = self.generate_id()
    def generate_id(self):
        if not self.tasks:
            return 1
        return max([task.id for task in self.tasks])+1
    def add_task(self, title: str, description: str = "", deadline: Optional[datetime] = None) -> Task:
        task = Task(id = self.next_id, title=title, description=description, deadline=deadline, status= Status.TODO, created_at=datetime.now())
        self.tasks.append(task)
        self.next_id +=1
        self.storage.save(self.tasks)
        return task

    def list_tasks(self, include_done: bool = True) -> List[Task]:
        tasks = self.tasks
        if not include_done:
            tasks = [t for t in tasks if not t.is_done()]
        return sorted(tasks, key=lambda t: (t.due_date is None, t.due_date))


    def get_due_soon(self, within_minutes: int = 30) -> List[Task]:
        now = datetime.now()
        threshold = now + timedelta(minutes=within_minutes)
        return [
            t
            for t in self.tasks
            if not t.is_done() and t.deadline and now <= t.deadline <= threshold
        ]