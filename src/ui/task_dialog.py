from datetime import datetime, date as date_, time as time_
from typing import Optional

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPlainTextEdit, QSpinBox, QCheckBox, QPushButton, QCalendarWidget, QMessageBox,
    QGraphicsOpacityEffect,
)

from src.model.task import Task, TaskType
from src.ui.time_wheel_picker import TimeWheelPicker


class TaskDialog(QDialog):
    """Единое окно создания/редактирования задачи.

    Все поля — название, описание, приоритет и (в зависимости от типа задачи)
    дедлайн с календарём/колёсиком времени, либо параметры повтора — видны
    одновременно, вместо цепочки отдельных QInputDialog/DeadlinePickerDialog.
    Используется и для создания новой задачи (task=None), и для редактирования
    существующей.
    """

    def __init__(self, parent=None, task_type: TaskType = TaskType.ONE_TIME, task: Optional[Task] = None):
        super().__init__(parent)
        self.task_type = task_type
        self._editing = task is not None

        if self._editing:
            title_text = "Редактирование задачи"
        elif task_type == TaskType.RECURRING:
            title_text = "Новая постоянная задача"
        else:
            title_text = "Новая задача"
        self.setWindowTitle(title_text)
        self.setMinimumWidth(380)
        self.setModal(True)

        self.setStyleSheet("""
            QDialog {
                background-color: #EDEBF7;
            }
            QLabel {
                color: #2E2A3D;
                font-weight: 600;
                font-size: 12px;
            }
            QLineEdit, QPlainTextEdit, QSpinBox {
                background-color: #FFFFFF;
                border: 1px solid #E1DCF7;
                border-radius: 10px;
                padding: 6px 10px;
                color: #2E2A3D;
            }
            QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus {
                border: 1px solid #8B7FD9;
            }
            QSpinBox {
                padding-right: 26px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                subcontrol-origin: border;
                width: 20px;
                border: none;
                background: transparent;
            }
            QSpinBox::up-button {
                subcontrol-position: top right;
                margin: 2px 3px 0 0;
            }
            QSpinBox::down-button {
                subcontrol-position: bottom right;
                margin: 0 3px 2px 0;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #F1EEFC;
                border-radius: 4px;
            }
            QSpinBox::up-arrow {
                width: 0px;
                height: 0px;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 5px solid #8A85A3;
            }
            QSpinBox::down-arrow {
                width: 0px;
                height: 0px;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #8A85A3;
            }
            QSpinBox::up-arrow:disabled, QSpinBox::up-arrow:off {
                border-bottom-color: #D8D4EE;
            }
            QSpinBox::down-arrow:disabled, QSpinBox::down-arrow:off {
                border-top-color: #D8D4EE;
            }
            QCheckBox {
                color: #6E68A0;
                font-weight: 500;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 2px solid #C9C3E8;
                background: white;
            }
            QCheckBox::indicator:checked {
                background-color: #8B7FD9;
                border: 2px solid #8B7FD9;
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
            QPushButton#saveBtn {
                background-color: #8B7FD9;
                color: white;
            }
            QPushButton#saveBtn:hover {
                background-color: #7A6EC8;
            }
            QPushButton#saveBtn:pressed {
                background-color: #6B5FB8;
            }
            QCalendarWidget {
                background-color: #FFFFFF;
                border-radius: 16px;
            }
            QCalendarWidget QToolButton {
                color: #2E2A3D;
                background-color: transparent;
                font-weight: 600;
                border-radius: 8px;
                padding: 4px 8px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #F1EEFC;
            }
            QCalendarWidget QMenu {
                background-color: #FFFFFF;
            }
            QCalendarWidget QAbstractItemView:enabled {
                selection-background-color: #8B7FD9;
                selection-color: white;
                color: #2E2A3D;
                background-color: #FFFFFF;
                outline: none;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #C9C3E8;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #FFFFFF;
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
            }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)
        outer.setSpacing(14)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.title_edit = QLineEdit(task.title if task else "")
        self.title_edit.setPlaceholderText("Название задачи")
        form.addRow("Название", self.title_edit)

        self.description_edit = QPlainTextEdit(task.description if task else "")
        self.description_edit.setPlaceholderText("Описание (необязательно)")
        self.description_edit.setFixedHeight(70)
        form.addRow("Описание", self.description_edit)

        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(1, 10)
        self.priority_spin.setValue(task.priority if task else 1)
        form.addRow("Приоритет (1-10)", self.priority_spin)

        outer.addLayout(form)

        if task_type == TaskType.ONE_TIME:
            self.no_deadline_check = QCheckBox("Без дедлайна")
            outer.addWidget(self.no_deadline_check)

            self.calendar = QCalendarWidget()
            self.calendar.setGridVisible(False)
            self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
            self.calendar.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.SingleLetterDayNames)
            outer.addWidget(self.calendar)

            time_label = QLabel("Время")
            outer.addWidget(time_label)

            has_deadline = bool(task and task.deadline)
            initial_date = task.deadline.date() if has_deadline else date_.today()
            initial_time = task.deadline.time() if has_deadline else time_(12, 0, 0)
            self.calendar.setSelectedDate(QDate(initial_date.year, initial_date.month, initial_date.day))

            self.time_picker = TimeWheelPicker(initial_time)
            outer.addWidget(self.time_picker)

            # Календарь и колёсики времени включены по умолчанию всегда —
            # даже если у задачи ещё нет дедлайна (новая задача, либо
            # редактирование задачи без дедлайна). Иначе, если чекбокс
            # "Без дедлайна" стоит по умолчанию, поля дедлайна заблокированы
            # (QWidget.setEnabled(False)) и клики по календарю ни к чему
            # не приводят — пользователь не может выставить дедлайн, пока
            # вручную не снимет галочку.
            start_enabled = True if task is None else has_deadline
            self.no_deadline_check.setChecked(not start_enabled)
            self._set_deadline_fields_enabled(start_enabled)
            self.no_deadline_check.toggled.connect(self._toggle_deadline_fields)
        else:
            recurring_form = QFormLayout()
            recurring_form.setSpacing(10)
            recurring_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

            self.times_spin = QSpinBox()
            self.times_spin.setRange(1, 50)
            self.times_spin.setValue(task.times_per_day if task else 1)
            recurring_form.addRow("Раз в день", self.times_spin)

            self.interval_spin = QSpinBox()
            self.interval_spin.setRange(0, 1440)
            self.interval_spin.setSpecialValueText("Без уведомлений")
            self.interval_spin.setValue(
                task.notify_interval_minutes if (task and task.notify_interval_minutes) else 0
            )
            recurring_form.addRow("Уведомлять каждые N мин", self.interval_spin)

            outer.addLayout(recurring_form)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.cancel_btn = QPushButton("Отмена")
        self.save_btn = QPushButton("Сохранить" if self._editing else "Создать")
        self.save_btn.setObjectName("saveBtn")
        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.save_btn)
        outer.addLayout(btn_row)

        self.cancel_btn.clicked.connect(self.reject)
        self.save_btn.clicked.connect(self._on_save)

    def _set_deadline_fields_enabled(self, enabled: bool) -> None:
        self.calendar.setEnabled(enabled)
        self.time_picker.setEnabled(enabled)
        # Наши стили задают цвета текста напрямую, поэтому нативное
        # ":disabled" состояние Qt почти не отличается от активного —
        # без этого визуально не видно, что поля выключены.
        opacity = 1.0 if enabled else 0.4
        for widget in (self.calendar, self.time_picker):
            effect = widget.graphicsEffect()
            if not isinstance(effect, QGraphicsOpacityEffect):
                effect = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(effect)
            effect.setOpacity(opacity)

    def _toggle_deadline_fields(self, no_deadline: bool) -> None:
        self._set_deadline_fields_enabled(not no_deadline)

    def _on_save(self) -> None:
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Название обязательно", "Введите название задачи.")
            self.title_edit.setFocus()
            return
        self.accept()

    def get_values(self) -> dict:
        """Собирает введённые значения. Вызывать после exec() == Accepted."""
        values: dict[str, object] = {
            "title": self.title_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
            "priority": self.priority_spin.value(),
        }
        if self.task_type == TaskType.ONE_TIME:
            if self.no_deadline_check.isChecked():
                values["deadline"] = None
            else:
                qd = self.calendar.selectedDate()
                t = self.time_picker.get_time()
                values["deadline"] = datetime(qd.year(), qd.month(), qd.day(), t.hour, t.minute, t.second)
        else:
            values["times_per_day"] = self.times_spin.value()
            interval = self.interval_spin.value()
            values["notify_interval_minutes"] = interval if interval > 0 else None
        return values