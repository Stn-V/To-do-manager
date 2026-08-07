from datetime import datetime

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QInputDialog,
                               QSystemTrayIcon, QStyle, )

from src.background.notifier import DeadLineNotifier
from src.ui.task_widjet import TaskWidget
from src.model.task import TaskType, Task
from src.model.task_manager import TaskManager
from src.model.storage import Storage
from src.config import TASKS_FILE, RECURRING_TASKS_FILE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 420, 400)
        self.setWindowTitle("To-Do Manager")

        self.task_manager = TaskManager(
            Storage(str(TASKS_FILE)),
            Storage(str(RECURRING_TASKS_FILE)),
        )
        self.task_widgets: dict[int, TaskWidget] = {}

        central = QWidget()
        self.layout = QVBoxLayout()
        central.setLayout(self.layout)
        self.setCentralWidget(central)

        # список задач — отдельный вложенный layout, чтобы новые задачи
        # добавлялись выше кнопок, а не после них
        self.tasks_layout = QVBoxLayout()
        self.layout.addLayout(self.tasks_layout)

        self.render_tasks()

        btn_row = QHBoxLayout()
        self.add_one_time_btn = QPushButton("+ Разовая задача")
        self.add_recurring_btn = QPushButton("+ Постоянная задача")
        btn_row.addWidget(self.add_one_time_btn)
        btn_row.addWidget(self.add_recurring_btn)
        self.layout.addLayout(btn_row)

        self.add_one_time_btn.clicked.connect(self.add_one_time_task)
        self.add_recurring_btn.clicked.connect(self.add_recurring_task)

        self.ui_refresh_timer = QTimer(self)
        self.ui_refresh_timer.timeout.connect(self.refresh_all_widgets)
        self.ui_refresh_timer.start(30000)

        self.tray_icon = QSystemTrayIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation), self)

        self.tray_icon.setToolTip("To-Do Manager")
        self.tray_icon.show()

        self.notifier = DeadLineNotifier(self.task_manager, self.tray_icon)
        self.notifier.start()


    # ---------- отрисовка ----------

    def closeEvent(self, event):
        self.ui_refresh_timer.stop()
        self.notifier.stop()
        # выполненные разовые задачи остаются видимыми (зачёркнутыми) в течение
        # сессии, но удаляются насовсем при закрытии программы
        self.task_manager.purge_completed_one_time()
        super().closeEvent(event)

    def refresh_all_widgets(self) -> None:
        for widget in self.task_widgets.values():
            widget.refresh()

    def render_tasks(self) -> None:
        for task in self.task_manager.list_tasks():
            self._add_widget_for(task)

    def _add_widget_for(self, task: Task) -> None:
        widget = TaskWidget(task)
        self.tasks_layout.addWidget(widget)
        self.task_widgets[task.id] = widget
        widget.deleted.connect(self.task_delete)
        widget.edit_requested.connect(self.task_edit_requested)
        widget.status_changed.connect(self.task_status_changed)

    def _remove_widget(self, task_id: int) -> None:
        widget = self.task_widgets.pop(task_id, None)
        if widget is None:
            return
        self.tasks_layout.removeWidget(widget)
        widget.deleteLater()

    def add_one_time_task(self) -> None:
        title, ok = QInputDialog.getText(self, "Новая задача", "Название:")
        if not ok or not title.strip():
            return
        description, ok = QInputDialog.getMultiLineText(
            self, "Описание", "Описание задачи (можно оставить пустым):"
        )
        if not ok:
            return
        dt_text, ok = QInputDialog.getText(
            self, "Дедлайн", "Дедлайн (ДД.ММ.ГГГГ ЧЧ:ММ, можно оставить пустым):"
        )
        if not ok:
            return
        task = self.task_manager.add_task(
            title.strip(), description=description.strip(), deadline=self._parse_deadline(dt_text)
        )
        self._add_widget_for(task)

    def add_recurring_task(self) -> None:
        title, ok = QInputDialog.getText(self, "Новая постоянная задача", "Название:")
        if not ok or not title.strip():
            return
        description, ok = QInputDialog.getMultiLineText(
            self, "Описание", "Описание задачи (можно оставить пустым):"
        )
        if not ok:
            return
        times, ok = QInputDialog.getInt(
            self, "Сколько раз в день", "Раз в день:", value=1, minValue=1, maxValue=50
        )
        if not ok:
            return
        task = self.task_manager.add_recurring_task(
            title.strip(), description=description.strip(), times_per_day=times
        )
        self._add_widget_for(task)

    @staticmethod
    def _parse_deadline(text: str):
        text = text.strip()
        if not text:
            return None
        try:
            return datetime.strptime(text, "%d.%m.%Y %H:%M")
        except ValueError:
            return None

    # ---------- обработка сигналов от TaskWidget ----------

    def task_delete(self, task_id: int) -> None:
        self.task_manager.delete_task(task_id)
        self._remove_widget(task_id)

    def task_status_changed(self, task_id: int) -> None:
        self.task_manager.complete_task(task_id)
        task = self.task_manager.get_task(task_id)
        if task is None:
            # разовая задача выполнена и удалена TaskManager'ом
            self._remove_widget(task_id)
        else:
            # постоянная задача — просто обновляем счётчик "N/M раз сегодня"
            widget = self.task_widgets[task_id]
            widget.task = task
            widget.refresh()

    def task_edit_requested(self, task_id: int) -> None:
        task = self.task_manager.get_task(task_id)
        if task is None:
            return

        new_title, ok = QInputDialog.getText(
            self, "Редактирование задачи", "Название:", text=task.title
        )
        if not ok or not new_title.strip():
            return

        new_description, ok = QInputDialog.getMultiLineText(
            self, "Описание", "Описание задачи (можно оставить пустым):", text=task.description
        )
        if not ok:
            return

        if task.task_type == TaskType.ONE_TIME:
            current = task.deadline.strftime("%d.%m.%Y %H:%M") if task.deadline else ""
            dt_text, ok = QInputDialog.getText(
                self, "Дедлайн", "Дедлайн (ДД.ММ.ГГГГ ЧЧ:ММ, можно оставить пустым):",
                text=current,
            )
            if not ok:
                return
            self.task_manager.edit_task(
                task_id, title=new_title.strip(), description=new_description.strip(),
                deadline=self._parse_deadline(dt_text)
            )
        else:
            new_times, ok = QInputDialog.getInt(
                self, "Сколько раз в день", "Раз в день:",
                value=task.times_per_day, minValue=1, maxValue=50,
            )
            if not ok:
                return
            self.task_manager.edit_task(
                task_id, title=new_title.strip(), description=new_description.strip(),
                times_per_day=new_times
            )

        updated = self.task_manager.get_task(task_id)
        widget = self.task_widgets[task_id]
        widget.task = updated
        widget.refresh()