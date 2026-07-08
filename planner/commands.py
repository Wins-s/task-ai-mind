"""Business logic for the planner package.

Each function represents a user-facing command:
add a task, list tasks, mark one done, delete one.
"""

from planner.models import Task
from planner.storage import load_tasks, save_tasks


VALID_PRIORITIES = {"low", "medium", "high"}


def add_task(title: str, priority: str = "medium") -> Task:
    """Create a new task and save it to storage.

    Raises ValueError if priority is not one of low/medium/high.
    Returns the newly created Task.
    """
    if priority not in VALID_PRIORITIES:
        raise ValueError(
            f"Invalid priority '{priority}'. "
            f"Must be one of: {', '.join(sorted(VALID_PRIORITIES))}"
        )

    tasks = load_tasks()
    next_id = max((t.id for t in tasks), default=0) + 1

    new_task = Task(id=next_id, title=title, priority=priority)
    tasks.append(new_task)
    save_tasks(tasks)

    return new_task


def list_tasks() -> list[Task]:
    """Return all tasks from storage."""
    return load_tasks()


def mark_done(task_id: int) -> Task:
    """Mark the task with the given id as done.

    Raises ValueError if no task with such id exists.
    Returns the updated Task.
    """
    tasks = load_tasks()

    for task in tasks:
        if task.id == task_id:
            task.status = "done"
            save_tasks(tasks)
            return task

    raise ValueError(f"Task with id {task_id} not found")


def delete_task(task_id: int) -> Task:
    """Delete the task with the given id.

    Raises ValueError if no task with such id exists.
    Returns the deleted Task.
    """
    tasks = load_tasks()

    for i, task in enumerate(tasks):
        if task.id == task_id:
            removed = tasks.pop(i)
            save_tasks(tasks)
            return removed

    raise ValueError(f"Task with id {task_id} not found")