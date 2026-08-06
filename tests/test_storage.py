from src.model.task import Task, TaskType, Status
from datetime import datetime
from src.model.storage import Storage
import json

def test_ensure_exists(tmp_path):
    dir_path = tmp_path/"data"
    file_path = dir_path/"test.json"

    storage = Storage(file_path)
    assert dir_path.exists()
    assert file_path.exists()
    with open(file_path) as f:
        data = json.load(f)
    assert data == []

def test_load(tmp_path):
    dir_path = tmp_path/"data"
    file_path = dir_path/"test.json"
    storage = Storage(file_path)

    created_at = datetime.now()
    raw = [{"id" : 1, "title" : "Task", "status": Status.TODO.value, "description": "Task description", "deadline": None,
            "created_at": created_at.isoformat(), "task_type": TaskType.ONE_TIME.value, "times_per_day": 3, "completions_today": 0,
            "last_reset_date": None}]
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(raw, f)
    tasks = storage.load()
    assert len(tasks) == 1
    task = tasks[0]
    assert task.id == 1
    assert task.title == "Task"
    assert task.status == Status.TODO
    assert task.description == "Task description"
    assert task.times_per_day == 3
    assert task.completions_today == 0

def test_load_broken(tmp_path):
    dir_path = tmp_path/"data"
    file_path = dir_path/"test.json"
    storage = Storage(file_path)

    file_path.write_text("{broken file")
    tasks = storage.load()
    assert tasks == []
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == []

def test_save(tmp_path):
    dir_path = tmp_path/"data"
    file_path = dir_path/"test.json"
    task_created = datetime.now()
    storage = Storage(file_path)
    task = Task(id=1, title="Task", status=Status.TODO, description="Task description",
                deadline=None, created_at=task_created, task_type=TaskType.ONE_TIME, times_per_day=3,
                completions_today=0,
                last_reset_date=None)
    storage.save([task])

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert data[0]["id"] == 1
    assert data[0]["title"] == "Task"
    assert data[0]["status"] == Status.TODO.value
    assert data[0]["description"] == "Task description"
    assert data[0]["deadline"] is None
    assert data[0]["created_at"] == task_created.isoformat()
    assert data[0]["task_type"] == TaskType.ONE_TIME.value
    assert data[0]["times_per_day"] == 3
    assert data[0]["completions_today"] == 0
    assert data[0]["last_reset_date"] is None

def test_save_empty(tmp_path):
    file_path = tmp_path/"data"/"test.json"
    storage = Storage(file_path)
    storage.save([])
    with open(file_path) as f:
        data = json.load(f)
    assert data == []
