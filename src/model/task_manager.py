from datetime import datetime, timedelta, date
from typing import Optional, List
from model.task import Task, Status, TaskType
from model.storage import Storage
class TaskManager:
    def __init__(self, storage: Storage, recurring_storage: Storage):
        self.storage = storage
        self.recurring_storage = recurring_storage
        self.one_time_tasks: List[Task] = self.storage.load()
        self.recurring_tasks: List[Task] = self.recurring_storage.load()
        self.next_id = self.generate_id()

    def reset_recurring_if_new_day(self) -> None:
        """При каждом запуске программы: если наступил новый день — обнуляем счётчик
        выполнений у постоянных задач, чтобы они снова стали активными."""
        today = date.today()
        changed = False
        for task in self.recurring_tasks:
            if task.last_reset_date != today:
                task.completions_today = 0
                task.last_reset_date = today
                task.status = Status.TODO
                changed = True
        if changed:
            self.recurring_storage.save(self.recurring_tasks)

    def generate_id(self)-> int:
        all_ids = [t.id for t in self.one_time_tasks + self.recurring_tasks]
        return max(all_ids) + 1 if all_ids else 1

    def _find(self, task_id: int) -> Optional[Task]:
        for task in self.one_time_tasks + self.recurring_tasks:
            if task.id == task_id:
                return task
        return None

    def add_task(self, title: str, description: str = "", deadline: Optional[datetime] = None) -> Task:
        """Разовая задача — удаляется при выполнении или по истечении дедлайна."""
        task = Task(
            id=self.next_id,
            title=title,
            description=description,
            deadline=deadline,
            status=Status.TODO,
            created_at=datetime.now(),
            task_type=TaskType.ONE_TIME,
        )
        self.one_time_tasks.append(task)
        self.next_id += 1
        self.storage.save(self.one_time_tasks)
        return task

    def add_recurring_task(self, title: str, description: str = "", times_per_day: int = 1) -> Task:
        """Постоянная задача — появляется каждый день заново, нужно выполнить
        times_per_day раз в течение дня (например, попить воды x4)."""
        task = Task(
            id=self.next_id,
            title=title,
            description=description,
            status=Status.TODO,
            created_at=datetime.now(),
            task_type=TaskType.RECURRING,
            times_per_day=max(1, times_per_day),
            completions_today=0,
            last_reset_date=date.today(),
        )
        self.recurring_tasks.append(task)
        self.next_id += 1
        self.recurring_storage.save(self.recurring_tasks)
        return task

    def list_tasks(self, include_done: bool = True) -> List[Task]:
        tasks = self.one_time_tasks + self.recurring_tasks
        if not include_done:
            tasks = [t for t in tasks if not t.is_done()]
        return sorted(tasks, key=lambda t: (t.due_date is None, t.due_date))


    def get_due_soon(self, within_minutes: int = 30) -> List[Task]:
        now = datetime.now()
        threshold = now + timedelta(minutes=within_minutes)
        return [
            t
            for t in self.one_time_tasks
            if not t.is_done() and t.deadline and now <= t.deadline <= threshold
        ]