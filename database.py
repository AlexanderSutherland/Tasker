import sqlite3

from models import Task
from datetime import date
from datetime import datetime, timedelta



DATABASE = "tasker.db"


class Database:

    def __init__(self):

        self.connection = sqlite3.connect(
            DATABASE
        )

        self.create_table()


    def add_time_entry(
            self,
            task_id,
            start,
            end,
            duration
    ):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO time_entries
            (
                task_id,
                start_time,
                end_time,
                duration
            )

            VALUES (?,?,?,?)

            """,

            (
                task_id,
                start,
                end,
                duration
            )
        )

        self.connection.commit()

    def create_table(self):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (

                id TEXT PRIMARY KEY,

                title TEXT,

                project TEXT,

                due_date TEXT,

                impact INTEGER,

                effort INTEGER,

                blocking INTEGER,

                waiting INTEGER,

                status TEXT,

                notes TEXT

            )
            """
        )
        
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS time_entries (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                task_id TEXT,

                start_time TEXT,

                end_time TEXT,

                duration REAL

            )
            """
        )

        self.connection.commit()

    def add_task(self, task):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?,?)
            """,
            (

                task.id,

                task.title,

                task.project,

                task.due_date.isoformat(),

                task.impact,

                task.effort,

                int(task.blocking),

                int(task.waiting),

                task.status,

                task.notes

            )
        )

        self.connection.commit()

    def get_tasks(self):

        cursor = self.connection.cursor()

        cursor.execute(
            "SELECT * FROM tasks"
        )

        rows = cursor.fetchall()

        tasks = []

        for row in rows:

            tasks.append(

                Task(

                    id=row[0],

                    title=row[1],

                    project=row[2],

                    due_date=date.fromisoformat(row[3]),

                    impact=row[4],

                    effort=row[5],

                    blocking=bool(row[6]),

                    waiting=bool(row[7]),

                    status=row[8],

                    notes=row[9]

                )

            )

        return tasks

    def delete_task(self, task_id):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            DELETE FROM tasks
            WHERE id=?
            """,
            (task_id,)
        )

        self.connection.commit()

    # def get_project_hours(self):

    #     cursor = self.connection.cursor()

    #     cursor.execute(
    #         """
    #         SELECT
    #             tasks.project,
    #             SUM(time_entries.duration)

    #         FROM time_entries

    #         JOIN tasks
    #         ON time_entries.task_id = tasks.id

    #         GROUP BY tasks.project

    #         ORDER BY SUM(time_entries.duration) DESC

    #         """
    #     )


    #     rows = cursor.fetchall()


    #     project_hours = {}

    #     for project, hours in rows:

    #         project_hours[project] = hours or 0


    #     return project_hours


    def get_total_hours(self, period="all"):

        cursor = self.connection.cursor()

        if period == "today":

            start = datetime.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

        elif period == "week":

            today = datetime.now()

            start = (today - timedelta(days=today.weekday())).replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

        elif period == "month":

            today = datetime.now()

            start = today.replace(
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )

        else:
            start = None


        if start is None:

            cursor.execute(
                """
                SELECT SUM(duration)
                FROM time_entries
                """
            )

        else:

            cursor.execute(
                """
                SELECT SUM(duration)
                FROM time_entries
                WHERE start_time >= ?
                """,
                (start.isoformat(),)
            )

        result = cursor.fetchone()[0]

        return result or 0

    def get_project_hours(self, period="week"):

        cursor = self.connection.cursor()


        if period == "today":

            start = datetime.now().replace(
                hour=0,
                minute=0,
                second=0
            )


        elif period == "week":

            today = datetime.now()

            start = today - timedelta(
                days=today.weekday()
            )


        elif period == "month":

            today = datetime.now()

            start = today.replace(
                day=1
            )


        else:

            start = datetime.min



        cursor.execute(
            """
            SELECT
                tasks.project,
                SUM(time_entries.duration)

            FROM time_entries

            JOIN tasks
            ON time_entries.task_id = tasks.id

            WHERE time_entries.start_time >= ?

            GROUP BY tasks.project

            """,
            (
                start.isoformat(),
            )
        )


        results = cursor.fetchall()


        return dict(results)

    def update_task(self, task):

        cursor = self.connection.cursor()

        cursor.execute(
            """
            UPDATE tasks SET

            title=?,
            project=?,
            due_date=?,
            impact=?,
            effort=?,
            blocking=?,
            waiting=?,
            status=?,
            notes=?

            WHERE id=?

            """,

            (

                task.title,

                task.project,

                task.due_date.isoformat(),

                task.impact,

                task.effort,

                int(task.blocking),

                int(task.waiting),

                task.status,

                task.notes,

                task.id

            )
        )

        self.connection.commit()