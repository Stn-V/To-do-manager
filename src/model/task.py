from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional
class Status(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
@dataclass
class Task:
    id: int
    title: str
    status: Status
    description: str = ""
    deadline: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "status": self.status.value,
            "description": self.description,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "created_at": self.created_at.isoformat(),
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
        )
    def is_done(self) -> bool:
        return self.status == Status.COMPLETED
