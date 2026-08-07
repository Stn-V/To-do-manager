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
        self.timer.timeout.connect(self.check)
    def start(self) -> None:
        self.timer.start(DEADLINE_CHECK_INTERVAL_MS)
        self.check()
    def stop(self) -> None:
        self.timer.stop()
    def check(self) -> None:
        due_soon = self.task_manager.get_due_soon(within_minutes=DEADLINE_WINDOW_MINUTES)
        for task in due_soon:
            if task.id in self.already_notified:
                continue
            self.tray_icon.showMessage("Дедлайн скоро!",
                f"{task.title} — до {task.deadline:%H:%M}",
                QSystemTrayIcon.MessageIcon.Information,
                10000,)
            self.already_notified.add(task.id)
        existing_ids = {t.id for t in self.task_manager.list_tasks()}
        self.already_notified &= existing_ids
