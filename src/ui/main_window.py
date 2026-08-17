from datetime import datetime
from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QInputDialog,
                               QSystemTrayIcon, QStyle, QStackedWidget, )
from PySide6.QtGui import QFont
from src.background.notifier import DeadLineNotifier
from src.ui.task_widjet import TaskWidget
from src.ui.welcome_screen import WelcomeScreen
from src.ui.calendar_page import CalendarPage
from src.model.task import TaskType, Task
from src.model.task_manager import TaskManager
from src.model.storage import Storage
from src.config import TASKS_FILE, RECURRING_TASKS_FILE
from PySide6.QtWidgets import QComboBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 420, 500)
        self.setWindowTitle("To-Do Manager")
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet("""
            QMainWindow, QWidget#central {
                background-color: #EDEBF7;
            }
            QPushButton {
                background-color: #FFFFFF;
                border: none;
                border-radius: 14px;
                padding: 10px 16px;
                color: #2E2A3D;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #F3F1FB;
            }
            QPushButton:pressed {
                background-color: #8B7FD9;
                color: white;
            }
            QComboBox {
                background-color: #FFFFFF;
                border: none;
                border-radius: 14px;
                padding: 8px 12px;
                color: #2E2A3D;
            }
            QComboBox::drop-down {
                border: none;
            }
            QLabel {
                color: #2E2A3D;
            }
        """)

        self.task_manager = TaskManager(
            Storage(str(TASKS_FILE)),
            Storage(str(RECURRING_TASKS_FILE)),
        )
        self.task_widgets: dict[int, TaskWidget] = {}

        central = QWidget()
        central.setObjectName("central")
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(16, 16, 16, 16)
        self.layout.setSpacing(14)
        central.setLayout(self.layout)
        self.tasks_page = central  # страница "Задачи" внутреннего стека

        # список задач — отдельный вложенный layout, чтобы новые задачи
        # добавлялись выше кнопок, а не после них
        self.tasks_layout = QVBoxLayout()
        self.tasks_layout.setSpacing(10)
        self.tasks_layout.setContentsMargins(0, 0, 0, 4)
        self.layout.addLayout(self.tasks_layout)

        self.render_tasks()

        btn_row = QHBoxLayout()
        self.add_one_time_btn = QPushButton("+ Разовая задача")
        self.add_recurring_btn = QPushButton("+ Постоянная задача")
        btn_row.addWidget(self.add_one_time_btn)
        btn_row.addWidget(self.add_recurring_btn)
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("По дедлайну", "deadline")
        self.sort_combo.addItem("По приоритету", "priority")
        self.sort_combo.addItem("Вручную", "order")
        self.sort_combo.currentIndexChanged.connect(self.on_sort_mode_changed)
        btn_row.addWidget(self.sort_combo)
        self.layout.addLayout(btn_row)

        self.add_one_time_btn.clicked.connect(self.add_one_time_task)
        self.add_recurring_btn.clicked.connect(self.add_recurring_task)

        # ---------- страница "Календарь" ----------
        self.calendar_page = CalendarPage(self.task_manager)

        # ---------- внутренний стек: Задачи (0) / Календарь (1) ----------
        self.inner_stack = QStackedWidget()
        self.inner_stack.addWidget(self.tasks_page)
        self.inner_stack.addWidget(self.calendar_page)

        # ---------- нижняя панель-переключатель (как иконки внизу на референсе) ----------
        self.nav_tasks_btn = QPushButton("🏠  Задачи")
        self.nav_calendar_btn = QPushButton("📅  Календарь")
        for btn in (self.nav_tasks_btn, self.nav_calendar_btn):
            btn.setCheckable(True)
            btn.setObjectName("navBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(10, 8, 10, 8)
        nav_layout.setSpacing(8)
        nav_layout.addWidget(self.nav_tasks_btn)
        nav_layout.addWidget(self.nav_calendar_btn)

        self.nav_bar = QWidget()
        self.nav_bar.setObjectName("navBar")
        self.nav_bar.setLayout(nav_layout)
        self.nav_bar.setStyleSheet("""
            #navBar {
                background-color: #FFFFFF;
                border-top: 1px solid #E1DCF7;
            }
            QPushButton#navBtn {
                background-color: transparent;
                border-radius: 14px;
                padding: 8px 14px;
                color: #8A85A3;
                font-weight: 600;
            }
            QPushButton#navBtn:checked {
                background-color: #F1EEFC;
                color: #6E68A0;
            }
            QPushButton#navBtn:hover {
                background-color: #F3F1FB;
            }
        """)

        self.nav_tasks_btn.clicked.connect(self.switch_to_tasks)
        self.nav_calendar_btn.clicked.connect(self.switch_to_calendar)
        self.nav_tasks_btn.setChecked(True)  # по умолчанию открыта страница задач

        # ---------- "оболочка" приложения: стек страниц + нижняя панель ----------
        self.app_shell = QWidget()
        shell_layout = QVBoxLayout(self.app_shell)
        shell_layout.setContentsMargins(0, 0, 0, 0)
        shell_layout.setSpacing(0)
        shell_layout.addWidget(self.inner_stack, 1)
        shell_layout.addWidget(self.nav_bar)

        # ---------- внешний стек: Приветствие (0) / Оболочка приложения (1) ----------
        self.welcome_screen = WelcomeScreen()
        self.welcome_screen.start_clicked.connect(self.show_task_list)

        self.stacked = QStackedWidget()
        self.stacked.addWidget(self.welcome_screen)  # индекс 0 — приветствие
        self.stacked.addWidget(self.app_shell)        # индекс 1 — задачи/календарь + нав. панель
        self.setCentralWidget(self.stacked)

        self.ui_refresh_timer = QTimer(self)
        self.ui_refresh_timer.timeout.connect(self.refresh_all_widgets)
        self.ui_refresh_timer.start(30000)

        self.tray_icon = QSystemTrayIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation), self)

        self.tray_icon.setToolTip("To-Do Manager")
        self.tray_icon.show()

        self.notifier = DeadLineNotifier(self.task_manager, self.tray_icon)
        self.notifier.start()


    # ---------- приветственный экран / переключение ----------

    def show_task_list(self) -> None:
        self.stacked.setCurrentWidget(self.app_shell)

    def switch_to_tasks(self) -> None:
        self.inner_stack.setCurrentWidget(self.tasks_page)
        self.nav_tasks_btn.setChecked(True)
        self.nav_calendar_btn.setChecked(False)

    def switch_to_calendar(self) -> None:
        # пересчитываем подсветку/список на случай, если задачи менялись,
        # пока была открыта страница "Задачи"
        self.calendar_page.refresh()
        self.inner_stack.setCurrentWidget(self.calendar_page)
        self.nav_calendar_btn.setChecked(True)
        self.nav_tasks_btn.setChecked(False)

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
        widget.container_layout = self.tasks_layout
        self.tasks_layout.addWidget(widget)
        self.task_widgets[task.id] = widget
        widget.deleted.connect(self.task_delete)
        widget.edit_requested.connect(self.task_edit_requested)
        widget.status_changed.connect(self.task_status_changed)
        widget.decrement_requested.connect(self.task_decrement)
        widget.order_changed.connect(self.task_order_changed)

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
        priority, ok = QInputDialog.getInt(self, "Приоритет", "Приоритет (1–10):", value=1, minValue=1, maxValue=10)
        if not ok:
            return
        task = self.task_manager.add_task(
            title.strip(), description=description.strip(), deadline=self._parse_deadline(dt_text), priority=priority,
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
        priority, ok = QInputDialog.getInt(
            self, "Приоритет", "Приоритет (1–10):", value=1, minValue=1, maxValue=10
        )
        if not ok:
            return
        task = self.task_manager.add_recurring_task(
            title.strip(),
            description=description.strip(),
            times_per_day=times,
            priority=priority,
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
        new_priority, ok = QInputDialog.getInt(
            self, "Приоритет", "Приоритет (1–10):",
            value=task.priority, minValue=1, maxValue=10,
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
                deadline=self._parse_deadline(dt_text),
                priority = new_priority
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
                times_per_day=new_times,
                priority = new_priority
            )

        updated = self.task_manager.get_task(task_id)
        widget = self.task_widgets[task_id]
        widget.task = updated
        widget.refresh()

    def task_decrement(self, task_id: int) -> None:
        self.task_manager.decrement_task(task_id)
        task = self.task_manager.get_task(task_id)
        if task is not None:
            widget = self.task_widgets[task_id]
            widget.task = task
            widget.refresh()

    def task_order_changed(self, task_id: int, new_index: int) -> None:
        self.task_manager.sort_mode = "order"
        idx = self.sort_combo.findData("order")
        if idx != -1:
            self.sort_combo.blockSignals(True)
            self.sort_combo.setCurrentIndex(idx)
            self.sort_combo.blockSignals(False)
        self.task_manager.update_order(task_id, new_index)
        self._rerender_all_tasks()

    def _rerender_all_tasks(self) -> None:
        # удаляем все виджеты
        for widget in self.task_widgets.values():
            self.tasks_layout.removeWidget(widget)
            widget.deleteLater()
        self.task_widgets.clear()
        # создаём заново в новом порядке
        for task in self.task_manager.list_tasks():
            self._add_widget_for(task)

    def on_sort_mode_changed(self, index: int) -> None:
        mode = self.sort_combo.itemData(index)
        self.task_manager.sort_mode = mode
        self._rerender_all_tasks()