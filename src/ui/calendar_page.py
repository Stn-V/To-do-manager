from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QTextCharFormat, QColor, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QCalendarWidget, QListWidget, QListWidgetItem,
)

from src.model.task_manager import TaskManager


class CalendarPage(QWidget):
    """обычная страница, встроенная во внутренний
    QStackedWidget в MainWindow — переключается кнопкой в нижней панели."""

    def __init__(self, task_manager: TaskManager):
        super().__init__()
        self.task_manager = task_manager

        self.setObjectName("calendarPage")
        self.setStyleSheet("""
            #calendarPage {
                background-color: #EDEBF7;
            }
            QLabel {
                color: #2E2A3D;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QLabel("Календарь задач")
        header.setStyleSheet("font-size: 18px; font-weight: 700;")
        layout.addWidget(header)

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

        self.day_label = QLabel()
        self.day_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #6E68A0;")
        layout.addWidget(self.day_label)

        self.day_tasks_list = QListWidget()
        self.day_tasks_list.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E1DCF7;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 8px;
            }
            QListWidget::item:hover {
                background-color: #F1EEFC;
            }
        """)
        layout.addWidget(self.day_tasks_list, 1)

        self.calendar.selectionChanged.connect(self.on_date_selected)
        self.calendar.currentPageChanged.connect(self.highlight_deadlines)

        self.highlight_deadlines()
        self.on_date_selected()

    # ---------- вызывается снаружи (MainWindow) при каждом переключении на эту страницу ----------

    def refresh(self) -> None:
        """Пересчитать подсветку и список задач. Нужно вызывать при каждом
        показе страницы — за это время могли добавить/удалить/выполнить задачи
        на странице 'Задачи', а календарь об этом сам не узнает."""
        self.highlight_deadlines()
        self.on_date_selected()

    # ---------- отметки дней с дедлайнами ----------

    def highlight_deadlines(self) -> None:
        year = self.calendar.yearShown()
        month = self.calendar.monthShown()
        days_in_month = QDate(year, month, 1).daysInMonth()
        today = QDate.currentDate()

        bold_font = QFont()
        bold_font.setBold(True)

        deadline_format = QTextCharFormat()
        deadline_format.setBackground(QColor("#8B7FD9"))
        deadline_format.setForeground(QColor("white"))
        deadline_format.setFont(bold_font)

        overdue_format = QTextCharFormat()
        overdue_format.setBackground(QColor("#EF8C82"))
        overdue_format.setForeground(QColor("white"))
        overdue_format.setFont(bold_font)

        today_font = QFont()
        today_font.setBold(True)
        today_font.setUnderline(True)

        today_format = QTextCharFormat()
        today_format.setBackground(QColor("#E1DCF7"))
        today_format.setForeground(QColor("#4B3F91"))
        today_format.setFont(today_font)

        # какие дни этого месяца имеют дедлайн, и есть ли среди них просроченный
        deadline_days: dict[int, bool] = {}
        for task in self.task_manager.one_time_tasks:
            if not task.deadline:
                continue
            d = task.deadline.date()
            if d.year == year and d.month == month:
                deadline_days[d.day] = deadline_days.get(d.day, False) or task.is_expired()

        for day in range(1, days_in_month + 1):
            qdate = QDate(year, month, day)
            is_today = qdate == today

            if day in deadline_days:
                # день с дедлайном: берём цвет дедлайна/просрочки,
                # а если это ещё и сегодня — добавляем подчёркивание-маркер
                fmt = QTextCharFormat(overdue_format if deadline_days[day] else deadline_format)
                if is_today:
                    f = fmt.font()
                    f.setUnderline(True)
                    fmt.setFont(f)
            elif is_today:
                fmt = today_format
            else:
                fmt = QTextCharFormat()

            self.calendar.setDateTextFormat(qdate, fmt)

    # ---------- список задач на выбранный день ----------

    def on_date_selected(self) -> None:
        qdate = self.calendar.selectedDate()
        py_date = qdate.toPython()

        self.day_label.setText(f"Задачи на {py_date.strftime('%d.%m.%Y')}")
        self.day_tasks_list.clear()

        tasks_today = [
            t for t in self.task_manager.one_time_tasks
            if t.deadline and t.deadline.date() == py_date
        ]
        tasks_today.sort(key=lambda t: t.deadline)

        if not tasks_today:
            item = QListWidgetItem("Нет задач на этот день")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.day_tasks_list.addItem(item)
            return

        for task in tasks_today:
            status = "✓ выполнено" if task.is_done() else ("⚠ просрочено" if task.is_expired() else "")
            text = f"{task.title} — {task.deadline:%H:%M}"
            if status:
                text += f"   {status}"
            self.day_tasks_list.addItem(QListWidgetItem(text))