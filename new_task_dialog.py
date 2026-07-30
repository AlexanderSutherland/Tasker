from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QDateEdit,
    QTextEdit,
    QCheckBox,
    QPushButton,
    QHBoxLayout,
)

from PySide6.QtCore import QDate

from models import Task


class NewTaskDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("New Task")
        self.resize(400, 450)

        self.task = None

        self.setup_ui()


    def setup_ui(self):

        layout = QVBoxLayout(self)


        form = QFormLayout()


        self.title = QLineEdit()

        self.project = QLineEdit()


        self.due_date = QDateEdit()

        self.due_date.setDate(
            QDate.currentDate()
        )

        self.due_date.setCalendarPopup(True)


        self.impact = QSpinBox()
        self.impact.setRange(1, 5)
        self.impact.setValue(3)


        self.effort = QSpinBox()
        self.effort.setRange(1, 5)
        self.effort.setValue(3)


        self.blocking = QCheckBox(
            "Blocks another person"
        )


        self.waiting = QCheckBox(
            "Waiting on someone"
        )


        self.notes = QTextEdit()


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


        layout.addLayout(form)

        layout.addWidget(
            self.blocking
        )

        layout.addWidget(
            self.waiting
        )

        layout.addWidget(
            self.notes
        )


        buttons = QHBoxLayout()

        save = QPushButton("Save")
        cancel = QPushButton("Cancel")


        save.clicked.connect(
            self.create_task
        )

        cancel.clicked.connect(
            self.reject
        )


        buttons.addWidget(save)
        buttons.addWidget(cancel)


        layout.addLayout(buttons)


    def create_task(self):

        self.task = Task(

            title=self.title.text(),

            project=self.project.text(),

            due_date=self.due_date.date().toPython(),

            impact=self.impact.value(),

            effort=self.effort.value(),

            blocking=self.blocking.isChecked(),

            waiting=self.waiting.isChecked(),

            notes=self.notes.toPlainText()

        )


        self.accept()