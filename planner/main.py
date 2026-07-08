"""Command-line interface for the planner package.

Provides commands to add, list, mark done, and delete tasks.
"""

import argparse
import sys

from planner.commands import add_task, list_tasks, mark_done, delete_task


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="planner",
        description="A simple task planner CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument(
        "--priority",
        choices=["low", "medium", "high"],
        default="medium",
        help="Task priority (default: medium)",
    )

    # list
    subparsers.add_parser("list", help="List all tasks")

    # done
    done_parser = subparsers.add_parser("done", help="Mark a task as done")
    done_parser.add_argument("task_id", type=int, help="ID of the task to mark done")

    # delete
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", type=int, help="ID of the task to delete")

    return parser


def main() -> int:
    """Entry point for the CLI. Returns exit code."""
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "add":
            task = add_task(args.title, priority=args.priority)
            print(f"Added task #{task.id}: {task.title} ({task.priority})")

        elif args.command == "list":
            tasks = list_tasks()
            if not tasks:
                print("No tasks yet. Add one with: planner add \"...\"")
                return 0
            for t in tasks:
                marker = "✔" if t.status == "done" else " "
                print(f"[{marker}] #{t.id} [{t.priority}] {t.title}")

        elif args.command == "done":
            task = mark_done(args.task_id)
            print(f"Marked #{task.id} as done: {task.title}")

        elif args.command == "delete":
            task = delete_task(args.task_id)
            print(f"Deleted #{task.id}: {task.title}")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())