from PySide6.QtCore import Signal, Qt, QMimeData, QEvent
from PySide6.QtGui import QDragEnterEvent, QDrag, QMouseEvent, QColor
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QCheckBox, QWidget, QMessageBox,
    QVBoxLayout, QGraphicsDropShadowEffect,
)
from src.model.task import Task, TaskType

class TaskWidget(QWidget):
    # все сигналы отдают наружу id задачи — конкретные действия
    # (сохранение, удаление, изменение) выполняет TaskManager в MainWindow
    deleted = Signal(int)
    edit_requested = Signal(int)
    status_changed = Signal(int) #для многоразовых это +1
    decrement_requested = Signal(int) #для многолразовых это -1
    order_changed = Signal(int, int)

    def __init__(self, task: Task):
        super().__init__()
        self.task = task
        self.setAcceptDrops(True)
        self.container_layout = None

        self.checkBox = QCheckBox()
        self.checkBox.setStyleSheet("""
            QCheckBox::indicator {
                width: 22px;
                height: 22px;
                border-radius: 11px;
                border: 2px solid #C9C3E8;
                background: white;
            }
            QCheckBox::indicator:checked {
                background-color: #8B7FD9;
                border: 2px solid #8B7FD9;
            }
        """)
        self.task_label = QLabel()
        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: #8A85A3; font-size: 12px;")

        self.checkBox.stateChanged.connect(self.on_check)

        self.minus_btn = QPushButton("➖")
        self.counter_label = QLabel()
        self.plus_btn = QPushButton("➕")
        self.minus_btn.setFixedWidth(28)
        self.plus_btn.setFixedWidth(28)
        self.minus_btn.setToolTip("Отменить одно выполнение")
        self.plus_btn.setToolTip("Засчитать выполнение")
        self.minus_btn.clicked.connect(self.on_minus)
        self.plus_btn.clicked.connect(self.on_plus)

        self.view_btn = QPushButton("👁")
        self.edit_btn = QPushButton("✏️")
        self.delete_btn = QPushButton("🗑️")

        self.view_btn.setToolTip("Показать описание")
        self.view_btn.clicked.connect(self.view_btn_clicked)
        self.delete_btn.clicked.connect(self.delete_btn_clicked)
        self.edit_btn.clicked.connect(self.edit_btn_clicked)



        self.task_label.installEventFilter(self)
        self.info_label.installEventFilter(self)

        layout = QHBoxLayout()
        layout.addWidget(self.checkBox)
        layout.addWidget(self.minus_btn)
        layout.addWidget(self.plus_btn)
        layout.addWidget(self.counter_label)
        layout.addWidget(self.task_label)
        layout.addWidget(self.info_label)
        layout.addWidget(self.view_btn)
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.delete_btn)

        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        self.setObjectName("taskCard")
        self.setStyleSheet("""
            #taskCard {
                background-color: #FFFFFF;
                border-radius: 16px;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(139, 127, 217, 40))
        self.setGraphicsEffect(shadow)

        self.refresh()

    def refresh(self) -> None:
        self.task_label.setText(self.task.title)
        self.task_label.setToolTip(self.task.description if self.task.description else "Без описания")

        is_recurring = self.task.task_type == TaskType.RECURRING

        # переключение видимости
        self.checkBox.setVisible(not is_recurring)
        self.minus_btn.setVisible(is_recurring)
        self.plus_btn.setVisible(is_recurring)
        self.counter_label.setVisible(is_recurring)

        if is_recurring:
            self.info_label.setText("🔁 повтор ежедневно")
            self.counter_label.setText(
                f"{self.task.completions_today}/{self.task.times_per_day}"
            )

            done = self.task.is_done()
            self.plus_btn.setEnabled(not done)
            self.minus_btn.setEnabled(self.task.completions_today > 0)

        else:
            if self.task.deadline:
                self.info_label.setText(f"до {self.task.deadline:%d.%m %H:%M}")
            else:
                self.info_label.setText("без дедлайна")

            self.checkBox.blockSignals(True)
            self.checkBox.setChecked(self.task.is_done())
            self.checkBox.blockSignals(False)
            self.checkBox.setEnabled(not self.task.is_done())

        # оформление
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

    def view_btn_clicked(self) -> None:
        text = self.task.description.strip() if self.task.description else "Описание отсутствует"
        QMessageBox.information(self, self.task.title, text)
    def on_minus(self) -> None:
        self.decrement_requested.emit(self.task.id)
    def on_plus(self) -> None:
        self.status_changed.emit(self.task.id)
    def dragEnterEvent(self, event) -> None:
        event.acceptProposedAction()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_drag()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            self.start_drag()
            return True
        return super().eventFilter(obj, event)

    def start_drag(self) -> None:
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(str(self.task.id))
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.MoveAction)

    def dragEnterEvent(self, event) -> None:
        event.acceptProposedAction()

    def dragMoveEvent(self, event) -> None:
        event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        if self.container_layout is None:
            return
        dragged_id_text = event.mimeData().text()
        if not dragged_id_text.isdigit():
            return
        dragged_id = int(dragged_id_text)
        if dragged_id == self.task.id:
            return
        target_index = self.container_layout.indexOf(self)
        if target_index == -1:
            return
        self.order_changed.emit(dragged_id, target_index)
        event.acceptProposedAction()

