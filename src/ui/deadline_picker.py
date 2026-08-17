from datetime import datetime, date as date_, time as time_
from typing import Optional

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCalendarWidget, QPushButton,
)

from src.ui.time_wheel_picker import TimeWheelPicker


class DeadlinePickerDialog(QDialog):
    """Диалог выбора дедлайна: дата — кликом по календарю, время — колёсами
    часов/минут/секунд. Полностью заменяет ручной ввод текста вида
    'ДД.ММ.ГГГГ ЧЧ:ММ'. Если передан `current`, диалог открывается с уже
    выставленной датой/временем (используется при редактировании задачи)."""

    def __init__(self, parent=None, current: Optional[datetime] = None):
        super().__init__(parent)
        self.setWindowTitle("Дедлайн")
        self.setStyleSheet("""
            QDialog { background-color: #EDEBF7; }
            QLabel { color: #2E2A3D; }
        """)

        self._cleared = False  # True, если нажали "Без дедлайна"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("Выберите дедлайн")
        title.setStyleSheet("font-size: 16px; font-weight: 700;")
        layout.addWidget(title)

        # ---------- календарь для даты ----------
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(False)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.SingleLetterDayNames)
        self.calendar.setStyleSheet("""
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
        layout.addWidget(self.calendar)

        initial_date = current.date() if current else date_.today()
        initial_time = current.time() if current else time_(12, 0, 0)
        self.calendar.setSelectedDate(QDate(initial_date.year, initial_date.month, initial_date.day))

        # ---------- колесо для времени ----------
        time_label = QLabel("Время")
        time_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #6E68A0;")
        layout.addWidget(time_label)

        self.time_picker = TimeWheelPicker(initial_time)
        layout.addWidget(self.time_picker)

        # ---------- кнопки ----------
        btn_row = QHBoxLayout()

        self.clear_btn = QPushButton("Без дедлайна")
        self.cancel_btn = QPushButton("Отмена")
        self.ok_btn = QPushButton("Готово")

        for btn in (self.clear_btn, self.cancel_btn, self.ok_btn):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)

        for btn in (self.clear_btn, self.cancel_btn):
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: none;
                    border-radius: 14px;
                    padding: 10px 16px;
                    color: #2E2A3D;
                }
                QPushButton:hover { background-color: #F3F1FB; }
            """)

        self.ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B7FD9;
                color: white;
                border: none;
                border-radius: 14px;
                padding: 10px 20px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #7A6EC8; }
        """)

        btn_row.addWidget(self.clear_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addWidget(self.ok_btn)
        layout.addLayout(btn_row)

        self.clear_btn.clicked.connect(self._on_clear)
        self.cancel_btn.clicked.connect(self.reject)
        self.ok_btn.clicked.connect(self.accept)

    def _on_clear(self) -> None:
        self._cleared = True
        self.accept()

    def get_datetime(self) -> Optional[datetime]:
        """Вызывать после exec(), если результат — QDialog.DialogCode.Accepted.
        Возвращает None, если пользователь нажал 'Без дедлайна'."""
        if self._cleared:
            return None
        qd = self.calendar.selectedDate()
        t = self.time_picker.get_time()
        return datetime(qd.year(), qd.month(), qd.day(), t.hour, t.minute, t.second)