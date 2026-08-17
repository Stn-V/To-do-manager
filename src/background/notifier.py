from datetime import datetime, timedelta
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QSystemTrayIcon

from src.config import DEADLINE_CHECK_INTERVAL_MS, DEADLINE_WINDOW_MINUTES
from src.model.task_manager import TaskManager
class DeadLineNotifier:
    def __init__(self, task_manager: TaskManager, tray_icon: QSystemTrayIcon)->None:
        self.task_manager = task_manager
        self.tray_icon = tray_icon
        self.timer = QTimer()
        self.already_notified: set[int] = set()
        self.last_recurring_notify: dict[int, datetime] = {}
        self.timer.timeout.connect(self.check)
    def start(self) -> None:
        self.timer.start(DEADLINE_CHECK_INTERVAL_MS)
        self.check()
    def stop(self) -> None:
        self.timer.stop()

    def check(self) -> None:
        now = datetime.now()

        # --- разовые задачи: дедлайн скоро ---
        due_soon = self.task_manager.get_due_soon(within_minutes=DEADLINE_WINDOW_MINUTES)
        for task in due_soon:
            if task.id in self.already_notified:
                continue
            self.tray_icon.showMessage(
                "Дедлайн скоро!",
                f"{task.title} — до {task.deadline:%H:%M}",
                QSystemTrayIcon.MessageIcon.Information,
                10000,
            )
            self.already_notified.add(task.id)

        # --- recurring задачи: уведомления по интервалу ---
        for task in self.task_manager.get_recurring_to_notify():
            last_time = self.last_recurring_notify.get(task.id)
            interval = timedelta(minutes=task.notify_interval_minutes)

            if last_time is None or (now - last_time) >= interval:
                remaining = task.times_per_day - task.completions_today
                self.tray_icon.showMessage(
                    "Напоминание",
                    f"{task.title} — осталось {remaining} из {task.times_per_day}",
                    QSystemTrayIcon.MessageIcon.Information,
                    8000,
                )
                self.last_recurring_notify[task.id] = now

        # очистка устаревших id
        existing_ids = {t.id for t in self.task_manager.list_tasks()}
        self.already_notified &= existing_ids
        self.last_recurring_notify = {
            k: v for k, v in self.last_recurring_notify.items() if k in existing_ids
        }