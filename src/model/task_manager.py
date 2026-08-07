
from datetime import datetime, timedelta, date
from typing import Optional, List
from src.model.task import Task, Status, TaskType
from src.model.storage import Storage
class TaskManager:
    def __init__(self, storage: Storage, recurring_storage: Storage):
        self.storage = storage
        self.recurring_storage = recurring_storage
        self.one_time_tasks: List[Task] = self.storage.load()
        self.recurring_tasks: List[Task] = self.recurring_storage.load()
        self.reset_recurring_if_new_day()
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

    def complete_task(self, task_id: int) -> None:
        """Разовая задача при выполнении НЕ удаляется — просто получает статус COMPLETED.
        Постоянная — увеличивает счётчик выполнений на сегодня."""
        task = self._find(task_id)
        if task is None:
            return

        if task.task_type == TaskType.ONE_TIME:
            task.status = Status.COMPLETED
            self.storage.save(self.one_time_tasks)
        else:
            task.completions_today += 1
            if task.completions_today >= task.times_per_day:
                task.status = Status.COMPLETED
            self.recurring_storage.save(self.recurring_tasks)

    def get_task(self, task_id: int) -> Optional[Task]:
        return self._find(task_id)

    def purge_completed_one_time(self) -> None:
        """Удаляет выполненные разовые задачи. Вызывается при закрытии программы,
        чтобы в течение сессии выполненная задача была видна (зачёркнута),
        а при следующем запуске уже не отображалась."""
        before = len(self.one_time_tasks)
        self.one_time_tasks = [
            t for t in self.one_time_tasks if t.status != Status.COMPLETED
        ]
        if len(self.one_time_tasks) != before:
            self.storage.save(self.one_time_tasks)

    def edit_task(
            self,
            task_id: int,
            title: str,
            description: Optional[str] = None,
            deadline: Optional[datetime] = None,
            times_per_day: Optional[int] = None,
    ) -> None:
        """Редактирование задачи. Для ONE_TIME обновляется дедлайн (None — снять дедлайн),
        для RECURRING — сколько раз в день нужно выполнить."""
        task = self._find(task_id)
        if task is None:
            return

        task.title = title
        if description is not None:
            task.description = description

        if task.task_type == TaskType.ONE_TIME:
            task.deadline = deadline
            self.storage.save(self.one_time_tasks)
        else:
            if times_per_day is not None:
                task.times_per_day = max(1, times_per_day)
                if task.completions_today > task.times_per_day:
                    task.completions_today = task.times_per_day
            self.recurring_storage.save(self.recurring_tasks)

    def delete_task(self, task_id: int) -> None:
        """Ручное удаление задачи любого типа."""
        task = self._find(task_id)
        if task is None:
            return

        if task.task_type == TaskType.ONE_TIME:
            self.one_time_tasks.remove(task)
            self.storage.save(self.one_time_tasks)
        else:
            self.recurring_tasks.remove(task)
            self.recurring_storage.save(self.recurring_tasks)

    def list_tasks(self, include_done: bool = True) -> List[Task]:
        tasks = self.one_time_tasks + self.recurring_tasks
        if not include_done:
            tasks = [t for t in tasks if not t.is_done()]
        return sorted(tasks, key=lambda t: (t.deadline is None, t.deadline or datetime.max))


    def get_due_soon(self, within_minutes: int = 30) -> List[Task]:
        now = datetime.now()
        threshold = now + timedelta(minutes=within_minutes)
        return [
            t
            for t in self.one_time_tasks
            if not t.is_done() and t.deadline and now <= t.deadline <= threshold
        ]