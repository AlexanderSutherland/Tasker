from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QPushButton,
    QHBoxLayout
)


class Dashboard(QWidget):


    def __init__(
        self,
        refresh_callback=None,
        parent=None
    ):

        super().__init__(parent)

        self.refresh_callback = refresh_callback

        self.period = "week"

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


        # -------------------------
        # Time period buttons
        # -------------------------

        button_layout = QHBoxLayout()

        today_button = QPushButton("Today")
        week_button = QPushButton("This Week")
        month_button = QPushButton("This Month")
        all_button = QPushButton("All Time")


        today_button.clicked.connect(
            lambda: self.change_period("today")
        )

        week_button.clicked.connect(
            lambda: self.change_period("week")
        )

        month_button.clicked.connect(
            lambda: self.change_period("month")
        )

        all_button.clicked.connect(
            lambda: self.change_period("all")
        )


        button_layout.addWidget(today_button)
        button_layout.addWidget(week_button)
        button_layout.addWidget(month_button)
        button_layout.addWidget(all_button)


        layout.addLayout(
            button_layout
        )


        # -------------------------
        # Summary
        # -------------------------

        self.summary = QLabel()

        layout.addWidget(
            self.summary
        )


        # -------------------------
        # Project hours
        # -------------------------

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
        project_times,
        total_hours
    ):
        print("Updating dashboard...")
        print("Period:", self.period)

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

            Total Logged:
            {total_hours:.2f} hours
            """
                )


        text = ""

        for project, hours in project_times.items():

            bar = "█" * int(hours)

            text += (
                f"{project:<20}"
                f"{bar} "
                f"{hours:.2f} hrs\n"
            )


        self.project_hours.setText(
            text
        )

    def change_period(self, period):

        print("Period selected:", period)

        self.period = period

        if self.refresh_callback:
            self.refresh_callback()