from PySide6.QtWidgets import QMainWindow, QLabel
from PySide6.QtWidgets import ( QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox, QWidget)
from model.storage import Storage
from model.task_manager import TaskManager
from ui.task_widjet import TaskWidget
from datetime import datetime, timedelta

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 300, 300, 300)
        self.setWindowTitle("To-Do Manager")

        central = QWidget()
        self.layout = QVBoxLayout()
        central.setLayout(self.layout)
        self.setCentralWidget(central)
        self.task_widgets = []
        self.storage = Storage("tasks.json")
        self.task_manager = TaskManager(self.storage)
        task = self.task_manager.add_task(title= "Задача", description = "",deadline=datetime.now() + timedelta(minutes=30))
        widget = TaskWidget(task)
        self.layout.addWidget(widget)
        self.task_widgets.append(widget)
        widget.deleted.connect(self.task_delete)
        widget.edited.connect(self.task_edited)

        self.add_btn = QPushButton("Добавить задачу")
        self.layout.addWidget(self.add_btn)
        self.add_btn.clicked.connect(self.add_task)

    def task_delete(self, task):
        print("MainWindow удаляет задачу:", task)
        widget_del= None
        for widget in self.task_widgets:
            if widget.task == task:
                widget_del = widget
                break
        if widget_del is None:
            return
        self.layout.removeWidget(widget_del)
        widget_del.deleteLater()
        self.task_widgets.remove(widget_del)
        self.task_manager.tasks = [ t for t in self.task_manager.tasks if t.id != task.id]
        self.task_manager.storage.save(self.task_manager.tasks)

    def add_task(self):
        task = self.task_manager.add_task(title = "Новая задача",description = "",deadline = None)
        widget = TaskWidget(task)
        self.layout.addWidget(widget)
        self.task_widgets.append(widget)
        widget.deleted.connect(self.task_delete)
        widget.edited.connect(self.task_edited)

    def task_edited(self, task):
        print("MainWindow получил обновлённую задачу:", task)
        for widget in self.task_widgets:
            if widget.task == task:
                break
        self.task_manager.storage.save(self.task_manager.tasks)
