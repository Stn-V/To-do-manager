from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox, QWidget, QInputDialog)
from PySide6.QtGui import QFont
from model.task import Task, TaskType

class TaskWidget(QWidget):
    deleted = Signal(object)
    edit_requested = Signal(object)
    status_changed = Signal(object)

    def __init__(self, task):
        super().__init__()
        self.task = task
        self.checkBox = QCheckBox()
        self.task_label = QLabel()
        self.info_label = QLabel()

        self.checkBox.stateChanged.connect(self.on_check)

        self.edit_btn = QPushButton("✏️")
        self.delete_btn = QPushButton("🗑️")

        self.delete_btn.clicked.connect(self.delete_btn_clicked)
        self.edit_btn.clicked.connect(self.edit_btn_clicked)

        layout = QHBoxLayout()
        layout.addWidget(self.checkBox)
        layout.addWidget(self.task_label)
        layout.addWidget(self.info_label)
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.delete_btn)
        self.setLayout(layout)

        self.refresh()

    def refresh(self) -> None:
        """Перерисовать виджет по текущим данным self.task (без лишних сигналов)."""
        self.task_label.setText(self.task.title)

        if self.task.task_type == TaskType.RECURRING:
            self.info_label.setText(
                f"🔁 {self.task.completions_today}/{self.task.times_per_day} раз сегодня"
            )
        elif self.task.deadline:
            if self.task.is_expired():
                self.info_label.setText(f"⚠️ просрочено (было до {self.task.deadline:%d.%m %H:%M})")
            else:
                self.info_label.setText(f"до {self.task.deadline:%d.%m %H:%M}")
        else:
            self.info_label.setText("без дедлайна")

        self.checkBox.blockSignals(True)
        self.checkBox.setChecked(self.task.is_done())
        self.checkBox.blockSignals(False)

        if self.task.is_done():
            self.task_label.setStyleSheet("text-decoration: line-through; color: gray;")
        elif self.task.is_expired():
            self.task_label.setStyleSheet("color: red; font-weight: bold;")
        else:
            self.task_label.setStyleSheet("")

    def on_check(self, state) -> None:
        # галочку можно только ставить — «выполнить» задачу/отметить один
        # из повторов. Обратный сброс через чекбокс не предусмотрен —
        # состояние управляется TaskManager'ом и обновляется через refresh()
        if self.checkBox.isChecked():
            self.status_changed.emit(self.task.id)
        else:
            self.checkBox.blockSignals(True)
            self.checkBox.setChecked(True)
            self.checkBox.blockSignals(False)

    def delete_btn_clicked(self) -> None:
        self.deleted.emit(self.task.id)

    def edit_btn_clicked(self) -> None:
        self.edit_requested.emit(self.task.id)

