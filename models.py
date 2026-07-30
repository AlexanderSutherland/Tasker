from dataclasses import dataclass, field
import uuid
from datetime import date


@dataclass
class Task:

    id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    title: str = ""
    project: str = ""
    due_date: date = None

    impact: int = 3
    effort: int = 3

    blocking: bool = False
    waiting: bool = False

    status: str = "Open"

    notes: str = ""

    def priority_score(self):

        today = date.today()

        days_remaining = (
            self.due_date - today
        ).days


        # Urgency
        if days_remaining < 0:
            urgency = 10
        elif days_remaining == 0:
            urgency = 8
        elif days_remaining <= 3:
            urgency = 5
        else:
            urgency = 2


        score = (
            urgency
            + self.impact * 3
            + (5 if self.blocking else 0)
            - (4 if self.waiting else 0)
        )

        return score