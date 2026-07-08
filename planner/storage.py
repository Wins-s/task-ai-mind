"""Storage layer for the planner package.

Handles reading and writing tasks to a JSON file.
"""

import json
from dataclasses import asdict
from pathlib import Path

from planner.models import Task


TASKS_FILE = Path(__file__).parent / "tasks.json"


def load_tasks() -> list[Task]:
    """Load all tasks from the JSON storage file.

    Returns an empty list if the file does not exist yet.
    """
    if not TASKS_FILE.exists():
        return []

    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return [Task(**item) for item in data]


def save_tasks(tasks: list[Task]) -> None:
    """Save the given list of tasks to the JSON storage file."""
    data = [asdict(task) for task in tasks]

    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)