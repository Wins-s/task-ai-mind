# task-ai-mind

Task planner with AI-powered code analysis CLI.

This is a learning project that consists of two parts:
- **Planner** — a simple command-line task manager
- **Analyzer** — an AI-powered CLI tool that generates technical reports about Git repositories (coming next)

## Features

- Add tasks with priority (low/medium/high)
- List all tasks with visual status indicators
- Mark tasks as done
- Delete tasks by ID
- Persistent storage in JSON

## Installation

Clone the repository and set up a virtual environment:

    git clone git@github.com:Wins-s/task-ai-mind.git
    cd task-ai-mind
    python -m venv venv
    source venv/Scripts/activate

No third-party dependencies required for the planner.

## Usage

Add a task:

    python -m planner add "Buy milk" --priority high

List all tasks:

    python -m planner list

Mark a task as done:

    python -m planner done 1

Delete a task:

    python -m planner delete 1

See all available commands:

    python -m planner --help

## Project Structure

    task-ai-mind/
    ├── planner/              # Task planner package
    │   ├── __init__.py
    │   ├── __main__.py       # Entry point for `python -m planner`
    │   ├── main.py           # CLI argument parsing
    │   ├── commands.py       # Business logic (add/list/done/delete)
    │   ├── storage.py        # JSON persistence
    │   └── models.py         # Task dataclass
    ├── .gitignore
    ├── LICENSE
    └── README.md

## License

MIT — see [LICENSE](./LICENSE) for details.