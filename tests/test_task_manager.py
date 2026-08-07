import pytest
from datetime import datetime, timedelta, date

from src.model.task_manager import TaskManager
from src.model.task import Task, TaskType, Status
from src.model.storage import Storage


class MockStorage(Storage):
    def __init__(self, initial=None):
        self.data = initial or []
        self.save_calls = 0

    def load(self):
        return list(self.data)

    def save(self, tasks):
        self.data = list(tasks)
        self.save_calls += 1


@pytest.fixture
def storage():
    return MockStorage()


@pytest.fixture
def recurring_storage():
    return MockStorage()


@pytest.fixture
def manager(storage, recurring_storage):
    return TaskManager(storage, recurring_storage)


def test_task_manager_creation(manager, storage, recurring_storage):
    assert manager.storage == storage
    assert manager.recurring_storage == recurring_storage


def test_add_task(manager, storage):
    task = manager.add_task("Title", "Description")

    assert task.title == "Title"
    assert task.description == "Description"
    assert task.task_type == TaskType.ONE_TIME
    assert task.status == Status.TODO
    assert isinstance(task.created_at, datetime)
    assert storage.data[0].id == task.id
    assert storage.save_calls == 1


def test_add_recurring_task(manager, recurring_storage):
    task = manager.add_recurring_task("Title", "Description", times_per_day=3)

    assert task.title == "Title"
    assert task.description == "Description"
    assert task.times_per_day == 3
    assert task.completions_today == 0
    assert task.last_reset_date == date.today()  # было сравнение с datetime.today() — всегда False
    assert recurring_storage.data[0].id == task.id
    assert recurring_storage.save_calls == 1


def test_complete_task(manager, storage):
    task = manager.add_task("Title")
    assert task.status == Status.TODO

    manager.complete_task(task.id)

    assert task.status == Status.COMPLETED
    assert storage.data[0].id == task.id
    assert storage.save_calls == 2  # add_task + complete_task


def test_complete_recurring_task(manager):
    task = manager.add_recurring_task("Title", times_per_day=2)
    assert task.status == Status.TODO
    assert task.completions_today == 0

    manager.complete_task(task.id)
    assert task.status == Status.TODO
    assert task.completions_today == 1

    manager.complete_task(task.id)
    assert task.status == Status.COMPLETED
    assert task.completions_today == 2


def test_complete_task_nonexistent_id_does_nothing(manager):
    manager.complete_task(999)  # не должно падать


def test_get_task_found_and_not_found(manager):
    task = manager.add_task("Title")

    assert manager.get_task(task.id) is task
    assert manager.get_task(999) is None


def test_reset_recurring_if_new_day():
    yesterday = date.today() - timedelta(days=1)
    task = Task(
        id=1,
        title="Title",
        description="Description",
        status=Status.COMPLETED,
        times_per_day=3,
        completions_today=3,
        last_reset_date=yesterday,
        task_type=TaskType.RECURRING,
        created_at=datetime.now(),
    )
    # Задачу нужно положить в хранилище ДО создания TaskManager —
    # сброс вызывается автоматически в __init__.
    recurring_storage = MockStorage(initial=[task])
    storage = MockStorage()

    TaskManager(storage, recurring_storage)

    assert task.status == Status.TODO
    assert task.completions_today == 0
    assert task.last_reset_date == date.today()


def test_reset_recurring_if_new_day_leaves_current_day_untouched(manager):
    task = manager.add_recurring_task("Title", times_per_day=3)
    manager.complete_task(task.id)
    manager.complete_task(task.id)

    manager.reset_recurring_if_new_day()

    assert task.completions_today == 2
    assert task.status == Status.TODO


def test_edit_task(manager):
    task = manager.add_task("Old_Title", "Old_Description")

    new_deadline = datetime.now() + timedelta(days=1)
    manager.edit_task(task.id, "New_Title", "New_Description", deadline=new_deadline)

    assert task.title == "New_Title"
    assert task.description == "New_Description"
    assert task.deadline == new_deadline


def test_edit_task_can_clear_deadline(manager):
    deadline = datetime.now() + timedelta(days=1)
    task = manager.add_task("Title", deadline=deadline)

    manager.edit_task(task.id, "Title", deadline=None)

    assert task.deadline is None


def test_edit_recurring_task(manager):
    task = manager.add_recurring_task("Old_Title", "Old_Description", times_per_day=3)

    manager.edit_task(task.id, "New_Title", "New_Description", times_per_day=4)

    assert task.title == "New_Title"
    assert task.description == "New_Description"
    assert task.times_per_day == 4
    assert task.completions_today == 0


def test_edit_recurring_task_clamps_completions_today(manager):
    task = manager.add_recurring_task("Title", times_per_day=5)
    task.completions_today = 5

    manager.edit_task(task.id, "Title", times_per_day=3)

    assert task.times_per_day == 3
    assert task.completions_today == 3


def test_edit_task_nonexistent_id_does_nothing(manager):
    manager.edit_task(999, "Doesn't matter")  # не должно падать


def test_delete_task(manager):
    t1 = manager.add_task("One")
    t2 = manager.add_recurring_task("Rec")

    manager.delete_task(t1.id)
    assert t1 not in manager.one_time_tasks

    manager.delete_task(t2.id)
    assert t2 not in manager.recurring_tasks


def test_delete_task_nonexistent_id_does_nothing(manager):
    manager.delete_task(999)  # не должно падать


def test_purge_completed_one_time_removes_only_completed(manager):
    t1 = manager.add_task("Task 1")
    t2 = manager.add_task("Task 2")
    manager.complete_task(t1.id)

    manager.purge_completed_one_time()

    assert t1 not in manager.one_time_tasks
    assert t2 in manager.one_time_tasks


def test_purge_completed_one_time_does_not_touch_recurring(manager):
    recurring = manager.add_recurring_task("Rec", times_per_day=1)
    manager.complete_task(recurring.id)

    manager.purge_completed_one_time()

    assert recurring in manager.recurring_tasks


def test_list_tasks(manager):
    soon = datetime.now() + timedelta(minutes=10)
    later = datetime.now() + timedelta(hours=2)

    t1 = manager.add_task("Soon", deadline=soon)
    t2 = manager.add_task("Later", deadline=later)
    t3 = manager.add_recurring_task("Recurring")  # без дедлайна

    tasks = manager.list_tasks()

    assert tasks[0] == t1
    assert tasks[1] == t2
    assert tasks[2] == t3  # задачи без дедлайна — в конце
    assert t3 in tasks


def test_list_tasks_excludes_done_when_requested(manager):
    todo = manager.add_task("Todo")
    done = manager.add_task("Done")
    manager.complete_task(done.id)

    tasks = manager.list_tasks(include_done=False)

    assert todo in tasks
    assert done not in tasks


def test_get_due_soon(manager):
    soon = datetime.now() + timedelta(minutes=10)
    later = datetime.now() + timedelta(hours=2)

    t1 = manager.add_task("Soon", deadline=soon)
    t2 = manager.add_task("Later", deadline=later)

    due = manager.get_due_soon(within_minutes=30)

    assert t1 in due
    assert t2 not in due


def test_get_due_soon_excludes_completed_and_no_deadline(manager):
    completed = manager.add_task("Completed", deadline=datetime.now() + timedelta(minutes=5))
    manager.complete_task(completed.id)
    no_deadline = manager.add_task("No deadline")

    due = manager.get_due_soon(within_minutes=30)

    assert completed not in due
    assert no_deadline not in due


def test_get_due_soon_ignores_recurring_tasks(manager):
    manager.add_recurring_task("Rec")

    due = manager.get_due_soon(within_minutes=60)

    assert due == []


def test_generate_id_uses_max_existing_id():
    storage = MockStorage()
    recurring_storage = MockStorage()
    manager1 = TaskManager(storage, recurring_storage)
    manager1.add_task("Task 1")
    manager1.add_recurring_task("Task 2")

    manager2 = TaskManager(storage, recurring_storage)

    assert manager2.next_id == 3