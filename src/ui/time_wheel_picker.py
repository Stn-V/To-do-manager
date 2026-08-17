from datetime import time as time_

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QAbstractItemView,
)


class _WheelColumn(QListWidget):
    """Одна прокручиваемая колонка чисел (0..max_value). Крутится колёсиком
    мыши, стрелками или перетаскиванием полосы прокрутки — выбранным
    считается значение, подсвеченное в центре колонки."""

    def __init__(self, max_value: int, initial: int = 0):
        super().__init__()
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setFixedWidth(64)
        self.setFixedHeight(190)  # видно примерно 5 строк одновременно
        self.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 8px 0px;
                font-size: 15px;
                color: #B7B2D6;
            }
            QListWidget::item:selected {
                background-color: #F1EEFC;
                color: #4B3F91;
                font-weight: 700;
                font-size: 18px;
                border-radius: 10px;
            }
        """)

        for value in range(max_value + 1):
            item = QListWidgetItem(f"{value:02d}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.addItem(item)

        self.setCurrentRow(initial)
        self.currentItemChanged.connect(lambda *_: self._center_current())

    def _center_current(self) -> None:
        item = self.currentItem()
        if item is not None:
            self.scrollToItem(item, QAbstractItemView.ScrollHint.PositionAtCenter)

    def showEvent(self, event) -> None:
        # при первом показе виджета центрируем выбранное значение —
        # без этого список может открыться проскроленным в самое начало
        super().showEvent(event)
        self._center_current()

    def value(self) -> int:
        item = self.currentItem()
        return int(item.text()) if item is not None else 0


class TimeWheelPicker(QWidget):
    """Выбор времени тремя колёсами: часы / минуты / секунды."""

    def __init__(self, initial: time_ | None = None):
        super().__init__()
        initial = initial or time_(12, 0, 0)

        self.hours_col = _WheelColumn(23, initial.hour)
        self.minutes_col = _WheelColumn(59, initial.minute)
        self.seconds_col = _WheelColumn(59, initial.second)

        columns_row = QHBoxLayout()
        columns_row.setSpacing(6)

        def wrap(column: _WheelColumn, label_text: str) -> QWidget:
            box = QWidget()
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(0, 0, 0, 0)
            box_layout.setSpacing(4)
            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #8A85A3; font-size: 11px; font-weight: 600;")
            box_layout.addWidget(column)
            box_layout.addWidget(label)
            return box

        columns_row.addWidget(wrap(self.hours_col, "Часы"))
        columns_row.addWidget(wrap(self.minutes_col, "Минуты"))
        columns_row.addWidget(wrap(self.seconds_col, "Секунды"))

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addLayout(columns_row)

    def get_time(self) -> time_:
        return time_(self.hours_col.value(), self.minutes_col.value(), self.seconds_col.value())