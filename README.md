# task-ai-mind

Learning project that combines a small task planner with an AI-powered GitHub repository analyzer, implemented as Claude Code skills.

The project has two parts:
- **Planner** — a dependency-free command-line task manager
- **Analyzer & Reporter** — GitHub API tooling exposed as Claude Code skills, so an AI agent can inspect any accessible repository and generate a technical report

## Features

### Planner
- Add tasks with priority (low/medium/high)
- List all tasks with visual status indicators
- Mark tasks as done
- Delete tasks by ID
- Persistent storage in JSON

### GitHub analyzer & reporter
- Fetch the recursive file/folder tree of any accessible repository via the GitHub REST API
- Read the content of a specific file
- Generate a structured Markdown report covering overview, tech stack, structure, strengths, areas for improvement, and recommendations
- Save the report under `output/report.md`

## Installation

Clone the repository and set up a virtual environment:

    git clone git@github.com:Wins-s/task-ai-mind.git
    cd task-ai-mind
    python -m venv venv
    source venv/Scripts/activate

Install Python dependencies:

    pip install -r requirements.txt

## Configuration

The analyzer requires a GitHub Personal Access Token to call the GitHub REST API. Create a `.env` file in the project root:

    GITHUB_TOKEN=github_pat_your_token_here

The token should be a **fine-grained** PAT with `Contents: Read-only` permission on the repositories you want to analyze. The `.env` file is ignored by Git and must never be committed.

The reporter workflow additionally requires [Claude Code](https://docs.claude.com/en/docs/claude-code) to be installed locally, since the skills are executed by the Claude Code agent.

## Usage

### Task Planner

Add a task:

    python -m planner add "Buy milk" --priority high

List all tasks:

    python -m planner list

Mark a task as done:

    python -m planner done 1

Delete a task:

    python -m planner delete 1

See all commands:

    python -m planner --help

### GitHub analyzer (standalone script)

Show the recursive file tree of a repository:

    python fetch_repo.py https://github.com/owner/repo

Show the content of a specific file:

    python fetch_repo.py https://github.com/owner/repo --file README.md
    python fetch_repo.py https://github.com/owner/repo --file src/main.py

### GitHub analyzer & reporter (via Claude Code)

The project ships two Claude Code skills under `.claude/skills/`:

- **`github-analyzer`** — inspects a repository (tree mode and file mode)
- **`repo-reporter`** — orchestrates `github-analyzer` to produce a full technical report

Run Claude Code inside the project root:

    claude

Then ask the agent in natural language, for example:

    Show me the structure of github.com/owner/repo
    Read the content of README.md in github.com/owner/repo
    Generate a technical report about github.com/owner/repo

For the last request, the agent will:
1. Fetch the repository tree via `github-analyzer`
2. Read several key files (README, dependency manifests, entry points)
3. Synthesize a report following a fixed Markdown template
4. Save it to `output/report.md`

An example report generated for this very project is available at [`output/report.md`](./output/report.md).

## Project Structure

    task-ai-mind/
    ├── .claude/
    │   └── skills/
    │       ├── github-analyzer/
    │       │   └── SKILL.md       # Fetches structure and file contents
    │       └── repo-reporter/
    │           └── SKILL.md       # Generates the full technical report
    ├── planner/                    # Task planner package
    │   ├── __init__.py
    │   ├── __main__.py             # Entry point for `python -m planner`
    │   ├── main.py                 # CLI argument parsing
    │   ├── commands.py             # Business logic (add/list/done/delete)
    │   ├── storage.py              # JSON persistence
    │   └── models.py               # Task dataclass
    ├── output/                     # Generated reports (ignored except .gitkeep)
    │   └── .gitkeep
    ├── fetch_repo.py               # GitHub REST API client used by the skills
    ├── .env                        # GitHub token (not committed)
    ├── .gitignore
    ├── LICENSE
    ├── README.md
    └── requirements.txt

## License

MIT — see [LICENSE](./LICENSE) for details.