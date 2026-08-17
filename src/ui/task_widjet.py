from PySide6.QtCore import Signal, Qt, QMimeData, QEvent
from PySide6.QtGui import QDragEnterEvent, QDrag, QMouseEvent, QColor
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton, QCheckBox, QWidget, QMessageBox,
    QVBoxLayout, QGraphicsDropShadowEffect, QFrame, QSizePolicy,
)
from src.model.task import Task, TaskType


class TaskWidget(QWidget):
    # все сигналы отдают наружу id задачи — конкретные действия
    # (сохранение, удаление, изменение) выполняет TaskManager в MainWindow
    deleted = Signal(int)
    edit_requested = Signal(int)
    status_changed = Signal(int)  # для многоразовых это +1
    decrement_requested = Signal(int)  # для многоразовых это -1
    order_changed = Signal(int, int)

    # цвет полоски приоритета: низкий -> зелёный, средний -> жёлтый, высокий -> красный
    _PRIORITY_COLORS = [
        (3, "#8FD9B6"),   # 1-3  низкий
        (6, "#F3C969"),   # 4-6  средний
        (10, "#EF8C82"),  # 7-10 высокий
    ]

    def __init__(self, task: Task):
        super().__init__()
        self.task = task
        self.setAcceptDrops(True)
        self.container_layout = None

        # ---------- полоска приоритета слева ----------
        self.priority_strip = QFrame()
        self.priority_strip.setFixedWidth(6)
        self.priority_strip.setObjectName("priorityStrip")

        # ---------- чекбокс / счётчик повторов ----------
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

        self.minus_btn = QPushButton("➖")
        self.counter_label = QLabel()
        self.counter_label.setObjectName("counterLabel")
        self.plus_btn = QPushButton("➕")
        self.minus_btn.setFixedSize(26, 26)
        self.plus_btn.setFixedSize(26, 26)
        self.minus_btn.setObjectName("miniBtn")
        self.plus_btn.setObjectName("miniBtn")
        self.minus_btn.setToolTip("Отменить одно выполнение")
        self.plus_btn.setToolTip("Засчитать выполнение")
        self.minus_btn.clicked.connect(self.on_minus)
        self.plus_btn.clicked.connect(self.on_plus)

        # ---------- текстовая часть ----------
        self.task_label = QLabel()
        self.task_label.setObjectName("taskTitle")

        self.info_label = QLabel()
        self.info_label.setObjectName("infoBadge")

        self.priority_label = QLabel()
        self.priority_label.setObjectName("priorityBadge")

        self.checkBox.stateChanged.connect(self.on_check)

        # ---------- кнопки действий ----------
        self.view_btn = QPushButton("👁")
        self.edit_btn = QPushButton("✏️")
        self.delete_btn = QPushButton("🗑️")
        for btn in (self.view_btn, self.edit_btn, self.delete_btn):
            btn.setObjectName("iconBtn")
            btn.setFixedSize(32, 32)

        self.view_btn.setToolTip("Показать описание")
        self.delete_btn.setToolTip("Удалить задачу")
        self.edit_btn.setToolTip("Редактировать задачу")
        self.view_btn.clicked.connect(self.view_btn_clicked)
        self.delete_btn.clicked.connect(self.delete_btn_clicked)
        self.edit_btn.clicked.connect(self.edit_btn_clicked)

        self.task_label.installEventFilter(self)
        self.info_label.installEventFilter(self)

        # ---------- раскладка ----------
        # верхняя строка: чекбокс/счётчик + заголовок + кнопки действий
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        top_row.addWidget(self.checkBox)
        top_row.addWidget(self.minus_btn)
        top_row.addWidget(self.counter_label)
        top_row.addWidget(self.plus_btn)
        top_row.addWidget(self.task_label, 1)
        top_row.addWidget(self.view_btn)
        top_row.addWidget(self.edit_btn)
        top_row.addWidget(self.delete_btn)

        # нижняя строка: бейджи с датой/повтором и приоритетом
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(8)
        bottom_row.addWidget(self.info_label)
        bottom_row.addWidget(self.priority_label)
        bottom_row.addStretch(1)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(14, 12, 14, 12)
        content_layout.setSpacing(8)
        content_layout.addLayout(top_row)
        content_layout.addLayout(bottom_row)

        content_widget = QWidget()
        content_widget.setLayout(content_layout)

        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        outer_layout.addWidget(self.priority_strip)
        outer_layout.addWidget(content_widget, 1)
        self.setLayout(outer_layout)

        self.setObjectName("taskCard")
        self.setStyleSheet("""
            #taskCard {
                background-color: #FFFFFF;
                border: 1px solid #E1DCF7;
                border-radius: 16px;
            }
            #taskCard:hover {
                border: 1px solid #B9AEEF;
            }
            #priorityStrip {
                border-top-left-radius: 16px;
                border-bottom-left-radius: 16px;
            }
            #taskTitle {
                font-size: 14px;
                font-weight: 600;
                color: #2E2A3D;
            }
            #infoBadge {
                background-color: #F1EEFC;
                color: #6E68A0;
                font-size: 11px;
                font-weight: 500;
                border-radius: 9px;
                padding: 3px 10px;
            }
            #priorityBadge {
                font-size: 11px;
                font-weight: 600;
                border-radius: 9px;
                padding: 3px 10px;
                color: white;
            }
            #counterLabel {
                font-size: 12px;
                font-weight: 600;
                color: #6E68A0;
                min-width: 32px;
                qproperty-alignment: AlignCenter;
            }
            QPushButton#miniBtn {
                border-radius: 13px;
                background-color: #F1EEFC;
                border: none;
                padding: 0px;
            }
            QPushButton#miniBtn:hover {
                background-color: #E1DCF7;
            }
            QPushButton#iconBtn {
                border-radius: 16px;
                background-color: transparent;
                border: none;
                padding: 0px;
            }
            QPushButton#iconBtn:hover {
                background-color: #F1EEFC;
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(22)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(139, 127, 217, 45))
        self.setGraphicsEffect(shadow)

        self.refresh()

    # ---------- вспомогательное ----------

    def _priority_color(self) -> str:
        for threshold, color in self._PRIORITY_COLORS:
            if self.task.priority <= threshold:
                return color
        return self._PRIORITY_COLORS[-1][1]

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
            self.info_label.setText(f"🔁  {self.task.completions_today}/{self.task.times_per_day} сегодня")
            self.counter_label.setText(f"{self.task.completions_today}/{self.task.times_per_day}")

            done = self.task.is_done()
            self.plus_btn.setEnabled(not done)
            self.minus_btn.setEnabled(self.task.completions_today > 0)
        else:
            if self.task.deadline:
                self.info_label.setText(f"🕒  до {self.task.deadline:%d.%m %H:%M}")
            else:
                self.info_label.setText("без дедлайна")

            self.checkBox.blockSignals(True)
            self.checkBox.setChecked(self.task.is_done())
            self.checkBox.blockSignals(False)
            self.checkBox.setEnabled(not self.task.is_done())

        # бейдж приоритета
        color = self._priority_color()
        self.priority_label.setText(f"★ {self.task.priority}")
        self.priority_label.setStyleSheet(f"""
            #priorityBadge {{
                background-color: {color};
                font-size: 11px;
                font-weight: 600;
                border-radius: 9px;
                padding: 3px 10px;
                color: white;
            }}
        """)
        # полоска слева
        self.priority_strip.setStyleSheet(f"""
            #priorityStrip {{
                background-color: {color};
                border-top-left-radius: 16px;
                border-bottom-left-radius: 16px;
            }}
        """)

        # оформление заголовка в зависимости от статуса
        if self.task.is_done():
            self.task_label.setStyleSheet("""
                #taskTitle { text-decoration: line-through; color: #A9A4C0; font-weight: 500; }
            """)
        elif self.task.is_expired():
            self.task_label.setStyleSheet("""
                #taskTitle { color: #D9534F; font-weight: 700; }
            """)
        else:
            self.task_label.setStyleSheet("""
                #taskTitle { color: #2E2A3D; font-weight: 600; }
            """)

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