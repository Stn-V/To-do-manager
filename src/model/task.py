from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, date
from typing import Optional
class Status(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
class TaskType(Enum):
    ONE_TIME = "one_time"
    RECURRING = "recurring"

@dataclass
class Task:
    id: int
    title: str
    status: Status
    description: str = ""
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    task_type: TaskType = TaskType.ONE_TIME
    times_per_day: int = 1  # сколько раз в день нужно выполнить (напр. попить воды x4)
    completions_today: int = 0  # сколько раз уже выполнено сегодня
    last_reset_date: Optional[date] = None  # когда последний раз обнулялся счётчик
    priority: int = 1 #1 = низкий, 5 = высокий
    order:int = 0 #позиция в списке при ручной сортировке

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "description": self.description,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "created_at": self.created_at.isoformat(),
            "task_type": self.task_type.value,
            "times_per_day": self.times_per_day,
            "completions_today": self.completions_today,
            "last_reset_date": self.last_reset_date.isoformat() if self.last_reset_date else None,
            "priority": self.priority,
            "order": self.order,
        }

    @classmethod
    def from_dict(cls,data: dict) -> "Task":
        return Task(
            id=data["id"],
            title=data["title"],
            status=Status(data["status"]),
            description=data["description"],
            deadline=datetime.fromisoformat(data["deadline"]) if data.get("deadline") else None,
            created_at=datetime.fromisoformat(data["created_at"]),
            task_type=TaskType(data.get("task_type", "one_time")),
            times_per_day=data.get("times_per_day", 1),
            completions_today=data.get("completions_today", 0),
            last_reset_date=date.fromisoformat(data["last_reset_date"]) if data.get("last_reset_date") else None,
            priority=data.get("priority", 1),
            order=data.get("order", 0),
        )

    def is_done(self) -> bool:
        if self.task_type == TaskType.RECURRING:
            return self.completions_today >= self.times_per_day
        return self.status == Status.COMPLETED

    def is_expired(self) -> bool:
        return (
                self.task_type == TaskType.ONE_TIME
                and self.deadline is not None
                and self.status != Status.COMPLETED
                and datetime.now() > self.deadline
        )