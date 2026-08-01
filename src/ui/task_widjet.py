from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox, QWidget, QInputDialog)
from PySide6.QtGui import QFont
from datetime import datetime

from model.task import Task


class TaskWidget(QWidget):
    deleted = Signal(object)
    edited = Signal(object)
    status_changed = Signal(object)

    def __init__(self, task):
        super().__init__()
        self.task = task
        self.checkBox = QCheckBox()
        self.task_label = QLabel(task.title)
        self.deadline_label = QLabel(task.deadline.strftime("%Y/%m/%d %H:%M:%S") if task.deadline else "No deadline")

        self.checkBox.stateChanged.connect(self.state_status)

        self.edit_btn = QPushButton("✏️")
        self.delete_btn = QPushButton("🗑️")

        self.delete_btn.clicked.connect(self.delete_btn_clicked)
        self.edit_btn.clicked.connect(self.edit_btn_clicked)

        layout = QHBoxLayout()
        layout.addWidget(self.checkBox)
        layout.addWidget(self.task_label)
        layout.addWidget(self.deadline_label)
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.delete_btn)
        self.setLayout(layout)


    def delete_btn_clicked(self ):
        print("Удаляем задачу:", self.task)
        self.deleted.emit(self.task)

    def edit_btn_clicked(self):
        print("Редактируем задачу:", self.task)
        new_title, ok = QInputDialog.getText(self,"Редактирование задачи", "Новое название:", text = self.task.title)
        if not ok:
            return
        current_deadline = (self.task.deadline.strftime("%Y/%m/%d %H:%M:%S")
        if self.task.deadline
        else ""
        )
        new_deadline_str, ok = QInputDialog.getText(
            self,
            "Редактирование дедлайна",
            "Новый дедлайн (YYYY/MM/DD HH:MM:SS):",
            text=current_deadline
        )
        if not ok:
            return
        self.task.title = new_title
        self.task.deadline = datetime.strptime(new_deadline_str, "%Y/%m/%d %H:%M:%S")
        self.task_label.setText(new_title)
        self.deadline_label.setText(new_deadline_str)
        self.edited.emit(self.task)

    def state_status(self, state ):
        if self.checkBox.isChecked():
            print("Задача выполнена ", self.task.title)
            self.task_label.setStyleSheet("text-decoration: line-through; color: gray;")
        else:
            print("Задача не выполнена ", self.task.title)
            self.task_label.setStyleSheet("")
        self.status_changed.emit(self.task)
