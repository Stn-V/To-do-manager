from src.model.task import Task, TaskType, Status
from datetime import datetime, timedelta

def test_task_creation():
    task = Task(id = 1, title= "Task", status= Status.TODO, description= "Task description",
                deadline= None, created_at= datetime.now(), times_per_day= 3, completions_today= 0,
                last_reset_date= None)
    assert task.id == 1
    assert task.title == "Task"
    assert task.status == Status.TODO
    assert task.description == "Task description"
    assert task.times_per_day == 3
    assert task.completions_today == 0

    assert task.task_type == TaskType.ONE_TIME
    assert isinstance(task.created_at, datetime)

def test_is_done_one_time():
    task = Task(id = 1, title= "Task", status= Status.TODO, description= "Task description",
                deadline= None, created_at= datetime.now(), times_per_day= 3, completions_today= 0,
                last_reset_date= None)
    assert task.is_done() is False

    task.status = Status.COMPLETED
    assert task.is_done() is True

def test_is_done_sev_time():
    task = Task(id = 1, title= "Task", status= Status.TODO, description= "Task description",
                deadline= None, created_at= datetime.now(), task_type=TaskType.RECURRING, times_per_day= 3, completions_today= 0,
                last_reset_date= None)
    assert task.is_done() is False

    task.completions_today = 2
    assert task.is_done() is False

    task.completions_today = 3
    assert task.is_done() is True

def test_is_expired():
    future_deadline = datetime.now() + timedelta(days=1)
    past_deadline = datetime.now() - timedelta(days=1)
    task = Task(id=1, title="Task", status=Status.TODO, description="Task description",
                deadline=None, created_at=datetime.now(), task_type=TaskType.ONE_TIME, times_per_day=3,
                completions_today=0,
                last_reset_date=None)
    assert task.is_expired() is False

    task.deadline = future_deadline
    assert task.is_expired() is False

    task.deadline = past_deadline
    assert task.is_expired() is True

    task.status = Status.COMPLETED
    assert task.is_expired() is False

def test_is_expired_sev_time():
    task = Task(id=1, title="Task", status=Status.TODO, description="Task description",
                deadline=None, created_at=datetime.now(), task_type=TaskType.RECURRING, times_per_day=3,
                completions_today=0,
                last_reset_date=None)
    assert task.is_expired() is False

def test_to_dict():
    task_created = datetime.now()
    task = Task(id=1, title="Task", status=Status.TODO, description="Task description",
                deadline=None, created_at=task_created, task_type=TaskType.ONE_TIME, times_per_day=3,
                completions_today=0,
                last_reset_date=None)
    data = task.to_dict()
    assert isinstance(data, dict)
    assert data["id"] == 1
    assert data["title"] == "Task"
    assert data["status"] == Status.TODO.value
    assert data["description"] == "Task description"
    assert data["deadline"] is None
    assert data["created_at"] == task_created.isoformat()
    assert data["task_type"] == TaskType.ONE_TIME.value
    assert data["times_per_day"] == 3
    assert data["completions_today"] == 0

def test_from_dict():
    task_created = datetime.now().isoformat()
    data = {"id": 1, "title" : "Task", "status": Status.TODO.value, "description": "Task description", "deadline": None,
            "created_at": task_created, "task_type": TaskType.ONE_TIME.value, "times_per_day": 3, "completions_today": 0,
            "last_reset_date": None}

    task = Task.from_dict(data)
    assert isinstance(task, Task)
    assert task.id == 1
    assert task.title == "Task"
    assert task.status == Status.TODO
    assert task.description == "Task description"
    assert task.deadline is None
    assert task.task_type == TaskType.ONE_TIME
    assert task.times_per_day == 3
    assert task.completions_today == 0
    assert task.last_reset_date is None

    assert isinstance(task.created_at, datetime)
    assert task.created_at.isoformat() == task_created
