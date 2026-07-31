from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox, QWidget, QInputDialog)
from PySide6.QtGui import QFont

class TaskWidget(QWidget):
    deleted = Signal(object)
    edited = Signal(object)
    status_changed = Signal(object)

    def __init__(self, task):
        super().__init__()
        self.task = task
        self.checkBox = QCheckBox()
        self.task_label = QLabel(self._get("task"))
        self.dedline_label = QLabel(self._get("dedline") or "No dedline")

        self.checkBox.stateChanged.connect(self.state_status)

        self.edit_btn = QPushButton("✏️")
        self.delete_btn = QPushButton("🗑️")

        self.delete_btn.clicked.connect(self.delete_btn_clicked)
        self.edit_btn.clicked.connect(self.edit_btn_clicked)

        layout = QHBoxLayout()
        layout.addWidget(self.checkBox)
        layout.addWidget(self.task_label)
        layout.addWidget(self.dedline_label)
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.delete_btn)
        self.setLayout(layout)

    def _get(self, task_field):
        try:
            return self.task.__getattribute__(task_field)
        except:
            pass
        try:
            return self.task[task_field]
        except:
            pass
        return None

    def delete_btn_clicked(self ):
        print("Удаляем задачу:", self.task)
        self.deleted.emit(self.task)

    def edit_btn_clicked(self):
        print("Редактируем задачу:", self.task)
        new_task, ok = QInputDialog.getText(self,"Редактирование задачи", "Новое название:", text = self._get("task"))
        if not ok:
            return
        new_dedline, ok = QInputDialog.getText(self, "Редактирование дедлайна", "Новый дедлайн:", text = self._get("dedline"))
        if not ok:
            return
        self.task["task"] = new_task
        self.task["dedline"] = new_dedline
        self.task_label.setText(new_task)
        self.dedline_label.setText(new_dedline)
        self.edited.emit(self.task)

    def state_status(self, state ):
        if self.checkBox.isChecked():
            print("Задача выполнена ", self._get("task"))
            self.task_label.setStyleSheet("text-decoration: line-through; color: gray;")
        else:
            print("Задача не выполнена ", self._get("task"))
            self.task_label.setStyleSheet("")
        self.status_changed.emit(self.task)

