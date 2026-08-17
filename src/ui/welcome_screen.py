from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class WelcomeScreen(QWidget):
    """Приветственный экран, который показывается при первом запуске окна.
    По нажатию 'Начать' MainWindow переключает QStackedWidget на список задач."""

    start_clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setObjectName("welcomeScreen")
        self.setStyleSheet("""
            #welcomeScreen {
                background-color: #EDEBF7;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(14)
        layout.setContentsMargins(40, 40, 40, 40)

        icon_label = QLabel("🗓️")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 68px;")

        title = QLabel("To-Do Manager")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 26px;
            font-weight: 700;
            color: #2E2A3D;
        """)

        subtitle = QLabel("Планируйте задачи, отслеживайте дедлайны\nи не забывайте о важном")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            font-size: 13px;
            color: #8A85A3;
        """)

        self.start_btn = QPushButton("Начать")
        self.start_btn.setFixedWidth(220)
        self.start_btn.setFixedHeight(44)
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B7FD9;
                color: white;
                border: none;
                border-radius: 22px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7A6EC8;
            }
            QPushButton:pressed {
                background-color: #6B5FB8;
            }
        """)
        self.start_btn.clicked.connect(self.start_clicked.emit)

        layout.addStretch(2)
        layout.addWidget(icon_label)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(22)
        layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(3)