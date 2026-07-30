from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGroupBox,
)


class Dashboard(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()


    def setup_ui(self):

        layout = QVBoxLayout(self)


        title = QLabel(
            "Work Dashboard"
        )

        title.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )


        layout.addWidget(title)


        self.summary = QLabel()

        layout.addWidget(
            self.summary
        )


        project_box = QGroupBox(
            "Project Time"
        )

        project_layout = QVBoxLayout()

        self.project_hours = QLabel()

        project_layout.addWidget(
            self.project_hours
        )

        project_box.setLayout(
            project_layout
        )


        layout.addWidget(
            project_box
        )


        layout.addStretch()


    def update_dashboard(
        self,
        tasks,
        project_times
    ):

        open_tasks = len(
            [
                t for t in tasks
                if t.status == "Open"
            ]
        )


        completed = len(
            [
                t for t in tasks
                if t.status == "Complete"
            ]
        )


        self.summary.setText(
            f"""
            Open Tasks: {open_tasks}

            Completed:
            {completed}
            """
        )


        text = ""

        for project, hours in project_times.items():

            text += (
                f"{project}: "
                f"{hours:.2f} hrs\n"
            )


        self.project_hours.setText(
            text
        )