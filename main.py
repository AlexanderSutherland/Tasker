import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QListWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QSplitter,
    QFormLayout,
    QCheckBox,
    QDateEdit,
    QSpinBox,
    QMessageBox,
    QTabWidget
)

from dashboard import Dashboard

from dataclasses import dataclass, field
import uuid

from datetime import date, timedelta

from models import Task
from priority import sort_tasks
from new_task_dialog import NewTaskDialog
from database import Database

from PySide6.QtCore import QTimer
from datetime import datetime

from PySide6.QtCore import Qt


class TaskManager(QMainWindow):

    def __init__(self):
        super().__init__()
        
        self.database = Database()
        self.tasks = []
        self.selected_task = None

        # Timer State        
        self.timer = QTimer()
        self.timer_running = False

        self.timer.timeout.connect(self.update_timer)

        self.timer_start = None
        self.elapsed_seconds = 0
        
        


        self.setWindowTitle("TaskPilot")
        self.resize(1400, 850)

        self.setup_ui()
        self.load_tasks()

    def start_timer(self):

        if self.selected_task is None:
            return

        if self.timer_running:
            return

        self.timer_start = datetime.now()

        self.elapsed_seconds = 0

        self.timer_running = True

        self.timer_label.setText(
            "🟢 00:00:00"
        )

        self.timer.start(1000)

    def update_timer(self):

        self.elapsed_seconds += 1

        hours = self.elapsed_seconds // 3600

        minutes = (
            self.elapsed_seconds % 3600
        ) // 60

        seconds = (
            self.elapsed_seconds % 60
        )


        self.timer_label.setText(
            f"🟢 {hours:02}:{minutes:02}:{seconds:02}"
        )

    def stop_timer(self):

        if not self.timer_running:
            return


        self.timer.stop()

        end = datetime.now()

        duration = (
            end - self.timer_start
        ).total_seconds() / 3600


        self.database.add_time_entry(
            self.selected_task.id,
            self.timer_start.isoformat(),
            end.isoformat(),
            duration
        )


        self.timer_running = False

        self.timer_label.setText(
            "⚪ 00:00:00"
        )

        self.timer_start = None

        self.update_dashboard()

    def load_tasks(self):
        self.tasks = self.database.get_tasks()
        self.refresh_table()
        self.update_dashboard()

    def new_task(self):

        dialog = NewTaskDialog(self)

        if dialog.exec():

            task = dialog.task

            if task:
                self.database.add_task(task)

                self.tasks.append(task)

                self.refresh_table()

    def complete_task(self):

        if self.selected_task is None:
            return


        self.selected_task.status = "Complete"


        self.database.update_task(
            self.selected_task
        )


        self.refresh_table()

        self.update_dashboard()

    def setup_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)


        # -------------------------
        # Top bar
        # -------------------------

        top_bar = QHBoxLayout()

        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Search tasks...")

        new_button = QPushButton("+ New Task")
        
        new_button.clicked.connect(
                                    self.new_task
                                )

        top_bar.addWidget(self.search)
        top_bar.addWidget(new_button)

        main_layout.addLayout(top_bar)


        # -------------------------
        # Main splitter
        # -------------------------

        splitter = QSplitter()

        # Left navigation

        nav = QWidget()
        nav_layout = QVBoxLayout(nav)

        nav_layout.addWidget(QLabel("Filters"))

        filters = [
            "Today",
            "This Week",
            "Overdue",
            "Waiting",
            "Backlog",
            "Completed",
        ]

        for item in filters:
            button = QPushButton(item)
            nav_layout.addWidget(button)

        nav_layout.addStretch()

        splitter.addWidget(nav)


        # Center task table

        self.table = QTableWidget()

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels(
            [
                "Score",
                "Task",
                "Due",
                "Project",
                "Status",
            ]
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        splitter.addWidget(self.table)
        
        self.table.cellClicked.connect(
                self.select_task
            )


        # Right detail panel

        details = QWidget()
        detail_layout = QVBoxLayout(details)

        detail_layout.addWidget(QLabel("Task Details"))

        self.selected_task = None

        self.title = QLineEdit()

        self.project = QLineEdit()

        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)

        self.impact = QSpinBox()
        self.impact.setRange(1,5)

        self.effort = QSpinBox()
        self.effort.setRange(1,5)

        self.blocking = QCheckBox(
            "Blocks other people"
        )

        self.waiting = QCheckBox(
            "Waiting on someone"
        )

        self.notes = QTextEdit()
        form = QFormLayout()

        form.addRow(
            "Title",
            self.title
        )

        form.addRow(
            "Project",
            self.project
        )

        form.addRow(
            "Due",
            self.due_date
        )

        form.addRow(
            "Impact",
            self.impact
        )

        form.addRow(
            "Effort",
            self.effort
        )

        form.addRow(
            self.blocking
        )

        form.addRow(
            self.waiting
        )


        detail_layout.addLayout(form)

        detail_layout.addWidget(
            QLabel("Notes")
        )

        detail_layout.addWidget(
            self.notes
        )

        save = QPushButton("Save")

        save.clicked.connect(self.save_task)

        delete = QPushButton("Delete")

        delete.clicked.connect(
            self.delete_task
        )


        complete = QPushButton("✓ Complete")
        
        complete.clicked.connect(
            self.complete_task
        )
        detail_layout.addWidget(save)

        detail_layout.addWidget(delete)
        
        detail_layout.addWidget(complete)
        

        
        self.start_button = QPushButton(
            "▶ Start Timer"
        )

        self.stop_button = QPushButton(
            "■ Stop Timer"
        )

        self.timer_label = QLabel(
            "00:00:00"
        )


        self.start_button.clicked.connect(
            self.start_timer
        )

        self.stop_button.clicked.connect(
            self.stop_timer
        )


        detail_layout.addWidget(
            self.timer_label
        )

        detail_layout.addWidget(
            self.start_button
        )

        detail_layout.addWidget(
            self.stop_button
        )
        

        splitter.addWidget(details)


        splitter.setSizes(
            [
                200,
                800,
                400
            ]
        )

        self.tabs = QTabWidget()


        self.task_tab = QWidget()

        task_layout = QVBoxLayout(
            self.task_tab
        )

        task_layout.addWidget(
            splitter
        )


        self.dashboard = Dashboard(refresh_callback=self.update_dashboard)


        self.tabs.addTab(
            self.task_tab,
            "Tasks"
        )


        self.tabs.addTab(
            self.dashboard,
            "Dashboard"
        )


        main_layout.addWidget(
            self.tabs
        )


        self.apply_theme()

    def update_dashboard(self):
        
        period = self.dashboard.period

        project_times = (
            self.database.get_project_hours()
        )

        total_hours = (
            self.database.get_total_hours()
        )

        # placeholder until we query database
        for task in self.tasks:

            project_times.setdefault(
                task.project,
                0
            )


        self.dashboard.update_dashboard(
            self.tasks,
            project_times,
            total_hours
        )

    def update_timer(self):

        self.elapsed_seconds += 1

        hours = self.elapsed_seconds // 3600

        minutes = (
            self.elapsed_seconds % 3600
        ) // 60

        seconds = (
            self.elapsed_seconds % 60
        )


        self.timer_label.setText(
            f"{hours:02}:{minutes:02}:{seconds:02}"
        )
        
    def stop_timer(self):

        if self.timer_start is None:
            return


        self.timer.stop()


        end = datetime.now()

        duration = (
            end - self.timer_start
        ).total_seconds() / 3600


        self.database.add_time_entry(
            self.selected_task.id,
            self.timer_start.isoformat(),
            end.isoformat(),
            duration
        )


        self.timer_start = None
        
    def start_timer(self):

        print("Start clicked")

        print(
            "Selected task:",
            self.selected_task
        )

        if self.selected_task is None:
            return


        self.timer_start = datetime.now()

        self.elapsed_seconds = 0

        self.timer.start(1000)

    def load_mock_tasks(self):

        self.tasks = [

            Task(
                title="Review ClearCase changes",
                project="Radar",
                due_date=date.today(),
                impact=5,
                blocking=True
            ),

            Task(
                title="Fix build failure",
                project="ARES",
                due_date=date.today(),
                impact=5
            ),

            Task(
                title="Update requirements document",
                project="Systems",
                due_date=date.today()+timedelta(days=3),
                impact=3
            ),

            Task(
                title="Write documentation",
                project="Docs",
                due_date=date.today()+timedelta(days=10),
                impact=1
            ),
        ]


        self.tasks = sort_tasks(self.tasks)


        self.table.setRowCount(len(self.tasks))

        for row, task in enumerate(self.tasks):
            values = [
                task.priority_score(),
                task.title,
                task.due_date,
                task.project,
                task.status
            ]


            for col,value in enumerate(values):

                self.table.setItem(
                    row,
                    col,
                    QTableWidgetItem(str(value))
                )

    def delete_task(self):

        if self.selected_task is None:
            return


        answer = QMessageBox.question(
            self,
            "Delete Task",
            f"Delete '{self.selected_task.title}'?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )


        if answer != QMessageBox.StandardButton.Yes:
            return


        self.database.delete_task(
            self.selected_task.id
        )


        self.tasks.remove(
            self.selected_task
        )


        self.selected_task = None


        self.title.clear()
        self.project.clear()
        self.notes.clear()


        self.refresh_table()
        self.update_dashboard()

    def apply_theme(self):

        self.setStyleSheet(
            """
            QWidget {
                background-color: #1e1e1e;
                color: #dddddd;
                font-size: 14px;
            }

            QLineEdit, QTextEdit {
                background-color: #252526;
                border: 1px solid #3c3c3c;
                padding: 6px;
            }

            QPushButton {
                background-color: #333333;
                border-radius: 5px;
                padding: 8px;
            }

            QPushButton:hover {
                background-color: #444444;
            }

            QTableWidget {
                background-color: #252526;
                gridline-color: #333333;
            }

            QHeaderView::section {
                background-color: #333333;
                padding: 6px;
            }
            """
        )

    def select_task(self, row, column):
        
        print("Clicked row:", row)
        print("Task count:", len(self.tasks))
        print("Table rows:", self.table.rowCount())

        task = self.tasks[row]

        self.selected_task = task


        self.title.setText(
            task.title
        )

        self.project.setText(
            task.project
        )

        self.impact.setValue(
            task.impact
        )

        self.effort.setValue(
            task.effort
        )

        self.blocking.setChecked(
            task.blocking
        )

        self.waiting.setChecked(
            task.waiting
        )

        self.notes.setText(
            task.notes
        )
        
    def save_task(self):

        if self.selected_task is None:
            return

        self.selected_task.title = self.title.text()

        self.selected_task.project = self.project.text()

        self.selected_task.impact = self.impact.value()

        self.selected_task.effort = self.effort.value()

        self.selected_task.blocking = (
            self.blocking.isChecked()
        )

        self.selected_task.waiting = (
            self.waiting.isChecked()
        )

        self.selected_task.notes = (
            self.notes.toPlainText()
        )
        
        self.database.update_task(
                self.selected_task
            )

        # Recalculate priority and refresh table
        self.refresh_table()
        self.update_dashboard()
        
    def refresh_table(self):

        self.tasks = sort_tasks(self.tasks)

        self.table.clearContents()

        self.table.setRowCount(
            len(self.tasks)
        )

        for row, task in enumerate(self.tasks):

            values = [
                task.priority_score(),
                task.title,
                str(task.due_date),
                task.project,
                task.status
            ]

            for col, value in enumerate(values):

                item = QTableWidgetItem(str(value))

                # Customize status display
                if col == 4 and task.status == "Complete":
                    item.setText("✓ Complete")

                self.table.setItem(
                    row,
                    col,
                    item
                )

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = TaskManager()
    window.show()

    sys.exit(app.exec())
    
