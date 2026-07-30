from models import Task


def sort_tasks(tasks):

    return sorted(
        tasks,
        key=lambda x: x.priority_score(),
        reverse=True
    )