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
    QTabWidget,
    QHeaderView
)

from PySide6.QtCore import QDate

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
        self.filtered_tasks = []
        self.base_filtered_tasks = []
        self.completed_tasks = []
        self.current_filter = "all"
        self.selected_task = None
        self.selected_source = None
        

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
        self.show_details(False)
        self.update_button_visibility()

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

        all_tasks = self.database.get_tasks()

        self.tasks = [
            t for t in all_tasks
            if t.status != "Complete"
        ]

        self.completed_tasks = [
            t for t in all_tasks
            if t.status == "Complete"
        ]


        # Important for filters
        self.filtered_tasks = self.tasks.copy()


        self.refresh_table()

        self.refresh_completed_table()

        self.update_dashboard()

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

    def new_task(self):

        dialog = NewTaskDialog(self)

        if dialog.exec():

            task = dialog.task

            if task:

                self.database.add_task(task)

                self.tasks.append(task)

                self.filtered_tasks.append(task)

                self.refresh_table()

                self.update_dashboard()
    
    def select_task(self, row, column, source):

        self.selected_source = source

        if source == "active":
            task = self.filtered_tasks[row]
        else:
            task = self.completed_tasks[row]

        self.load_task_into_editor(task)
        self.load_task_into_editor(task)
        self.show_details(True)

        self.update_button_visibility()

    def save_editor_to_task(self, task):

        task.title = self.title.text()

        task.project = self.project.text()

        task.due_date = (
            self.due_date.date().toPython()
        )

        task.impact = self.impact.value()

        task.effort = self.effort.value()

        task.blocking = (
            self.blocking.isChecked()
        )

        task.waiting = (
            self.waiting.isChecked()
        )

        task.notes = (
            self.notes.toPlainText()
        )

    def save_task(self):

        if self.selected_task is None:
            return

        self.save_editor_to_task(self.selected_task)

        self.database.update_task(self.selected_task)

        self.refresh_table()
        self.update_dashboard()

    def complete_task(self):

        if self.selected_task is None:
            print("No selected task")
            return


        task = self.selected_task

        print("Completing:", task.title)


        task.status = "Complete"
        task.completed_date = date.today()


        # Save database first
        self.database.update_task(task)


        # Remove from active views
        self.tasks = [
            t for t in self.tasks
            if t.id != task.id
        ]

        self.filtered_tasks = [
            t for t in self.filtered_tasks
            if t.id != task.id
        ]


        # Add to completed
        self.completed_tasks.append(task)


        # Clear selection
        self.selected_task = None


        # Refresh UI
        self.refresh_table()
        self.refresh_completed_table()

        self.update_dashboard()

    def delete_task(self):

        if self.selected_task is None:
            print("No selected task")
            return


        task = self.selected_task


        reply = QMessageBox.question(
            self,
            "Delete Task",
            f"Are you sure you want to delete:\n\n{task.title}?",
            QMessageBox.StandardButton.Yes |
            QMessageBox.StandardButton.No
        )


        if reply != QMessageBox.StandardButton.Yes:
            return


        print("Deleting:", task.title)


        self.database.delete_task(task.id)


        self.tasks = [
            t for t in self.tasks
            if t.id != task.id
        ]

        self.filtered_tasks = [
            t for t in self.filtered_tasks
            if t.id != task.id
        ]

        self.completed_tasks = [
            t for t in self.completed_tasks
            if t.id != task.id
        ]



        self.selected_task = None
        self.selected_source = None
        self.clear_editor()
        self.show_details(False)
        self.update_button_visibility()

        self.refresh_table()

        self.refresh_completed_table()

        self.update_dashboard()
        
    def reopen_task(self):

        row = self.completed_table.currentRow()

        if row < 0:
            return


        task = self.completed_tasks[row]


        task.status = "Open"

        task.completed_date = None


        self.database.update_task(task)


        self.completed_tasks.remove(task)

        self.tasks.append(task)

        self.filtered_tasks.append(task)


        self.refresh_table()

        self.refresh_completed_table()

        self.update_dashboard()

    def load_task_into_editor(self, task):

        self.selected_task = task

        self.title.setText(task.title)

        self.project.setText(task.project)

        self.due_date.setDate(
            QDate(
                task.due_date.year,
                task.due_date.month,
                task.due_date.day
            )
        )

        self.impact.setValue(task.impact)

        self.effort.setValue(task.effort)

        self.blocking.setChecked(task.blocking)

        self.waiting.setChecked(task.waiting)

        self.notes.setPlainText(task.notes)

    def clear_editor(self):

        self.title.clear()

        self.project.clear()

        self.due_date.setDate(
            QDate.currentDate()
        )

        self.impact.setValue(3)

        self.effort.setValue(3)

        self.blocking.setChecked(False)

        self.waiting.setChecked(False)

        self.notes.clear()

    def apply_filter(self, filter_name):

        self.current_filter = filter_name

        today = date.today()

        if filter_name == "all":

            self.filtered_tasks = self.tasks.copy()

        elif filter_name == "today":

            self.filtered_tasks = [
                t for t in self.tasks
                if t.due_date == today
            ]

        elif filter_name == "week":

            self.filtered_tasks = [
                t for t in self.tasks
                if 0 <= (t.due_date - today).days <= 7
            ]

        elif filter_name == "waiting":

            self.filtered_tasks = [
                t for t in self.tasks
                if t.waiting
            ]

        elif filter_name == "completed":

            self.filtered_tasks = [
                t for t in self.tasks
                if t.status == "Complete"
            ]
        self.base_filtered_tasks = self.filtered_tasks.copy()

        self.apply_search()
        self.refresh_table()

    def apply_search(self):

        text = self.search.text().lower().strip()
        if not text:
            self.filtered_tasks = (
                self.base_filtered_tasks.copy()
            )

        else:
            self.filtered_tasks = [
                task
                for task in self.base_filtered_tasks
                if (
                    text in task.title.lower()
                    or text in task.project.lower()
                    or text in task.notes.lower()
                )
            ]


        self.refresh_table()

    def show_details(self, visible):

        self.details_placeholder.setVisible(
            not visible
        )

        self.title.setVisible(
            visible
        )

        self.project.setVisible(
            visible
        )

        self.due_date.setVisible(
            visible
        )

        self.impact.setVisible(
            visible
        )

        self.effort.setVisible(
            visible
        )

        self.blocking.setVisible(
            visible
        )

        self.waiting.setVisible(
            visible
        )

        self.notes.setVisible(
            visible
        )

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
        self.search.textChanged.connect(
            self.apply_search
        )

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



        filter_map = {
            "Today": "today",
            "This Week": "week",
            "Overdue": "overdue",
            "Waiting": "waiting",
            "Backlog": "backlog",
            "Completed": "completed",
        }

        for text, filter_name in filter_map.items():
            button = QPushButton(text)
            button.clicked.connect(lambda checked=False, f=filter_name: self.apply_filter(f))
            nav_layout.addWidget(button)

        nav_layout.addStretch()

        splitter.addWidget(nav)

        # Center task table

        self.table = QTableWidget()

        self.table.setColumnCount(5)
        
        header = self.table.horizontalHeader()

        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Priority
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)           # Title
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Due Date
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)           # Project
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Status

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
            lambda row, col: self.select_task(row, col, "active")
        )
        
        # Center task area

        task_area = QWidget()

        task_layout = QVBoxLayout(task_area)


        task_layout.addWidget(
            QLabel("Active Tasks")
        )

        task_layout.addWidget(
            self.table
        )


        task_layout.addWidget(
            QLabel("Completed Tasks")
        )


        self.completed_table = QTableWidget()

        self.completed_table.setColumnCount(3)

        self.completed_table.setHorizontalHeaderLabels(
            [
                "Title",
                "Project",
                "Completed Date"
            ]
        )
        header = self.completed_table.horizontalHeader()

        header.setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch
        )  # Title

        header.setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Stretch
        )  # Project

        header.setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents
        )  # Completed Date
        
        
        self.completed_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        
        self.completed_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        task_layout.addWidget(
            self.completed_table
        )
        
        self.completed_table.cellClicked.connect(
            lambda row, col: self.select_task(row, col, "completed")
        )


        splitter.addWidget(
            task_area
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

        self.save_button = QPushButton("Save")

        self.save_button.clicked.connect(self.save_task)

        self.delete_button = QPushButton("Delete")

        self.delete_button.clicked.connect(
            self.delete_task
        )


        self.complete_button = QPushButton("✓ Complete")
        
        self.complete_button.clicked.connect(
            self.complete_task
        )
        
        self.reopen_button = QPushButton(
            "↩ Reopen"
        )

        self.reopen_button.clicked.connect(
            self.reopen_task
        )
        
        detail_layout.addWidget(self.save_button)

        detail_layout.addWidget(self.delete_button)
        
        detail_layout.addWidget(self.complete_button)
        
        detail_layout.addWidget(self.reopen_button)
        
        self.details_placeholder = QLabel(
            "Select a task to view details"
        )

        self.details_placeholder.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        
        detail_layout.addWidget(
            self.details_placeholder
        )
                
        
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

    def update_button_visibility(self):

        if self.selected_source == "active":

            self.save_button.show()

            self.delete_button.show()

            self.complete_button.show()

            self.reopen_button.hide()


        elif self.selected_source == "completed":

            self.save_button.hide()

            self.delete_button.show()

            self.complete_button.hide()

            self.reopen_button.show()


        else:

            self.save_button.hide()

            self.delete_button.hide()

            self.complete_button.hide()

            self.reopen_button.hide()

    def update_dashboard(self):

        period = self.dashboard.period

        project_times = self.database.get_project_hours(period)

        total_hours = self.database.get_total_hours(period)

        self.dashboard.update_dashboard(
            self.tasks,
            project_times,
            total_hours
        )

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

    def refresh_table(self):

        self.tasks = sort_tasks(self.tasks)

        self.table.clearContents()

        self.table.setRowCount(
            len(self.filtered_tasks)
        )

        for row, task in enumerate(self.filtered_tasks):

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

    def refresh_completed_table(self):

        self.completed_table.clearContents()

        self.completed_table.setRowCount(
            len(self.completed_tasks)
        )


        for row, task in enumerate(
            self.completed_tasks
        ):

            values = [
                task.title,
                task.project,
                task.completed_date
            ]

            for col, value in enumerate(values):

                self.completed_table.setItem(
                    row,
                    col,
                    QTableWidgetItem(str(value))
                )

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = TaskManager()
    window.show()

    sys.exit(app.exec())
    
