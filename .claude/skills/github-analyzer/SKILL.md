---
name: github-analyzer
description: Analyzes GitHub repositories via the REST API. Can fetch the recursive file/folder tree of a repository, or read the content of a specific file. Triggers on requests to inspect, describe, list files, show structure, show file content, read file, or analyze a GitHub repository — e.g. "show me the structure of github.com/user/repo", "list files in this GitHub repo", "show the content of README.md in <repo-url>", "read planner/main.py from <repo-url>".
allowed-tools: Bash(python:*), Bash(python3:*)
---

# GitHub Repository Analyzer

This skill inspects GitHub repositories through the REST API. It supports two operations:

1. **Tree mode** — fetch and print the recursive file/folder structure
2. **File mode** — fetch and print the content of a specific file

## Prerequisites

- A `GITHUB_TOKEN` environment variable must be present in the project's `.env` file. The token is a GitHub fine-grained Personal Access Token with `Contents: Read-only` permission on the target repository.
- The helper script `fetch_repo.py` must exist in the project root.
- Python dependencies (`requests`, `python-dotenv`) must be installed — they are listed in `requirements.txt`.

## Workflow

### When to use tree mode

When the user asks to see the **structure**, **list files**, or **inspect** a repository without pointing at a specific file.

Run:

    python fetch_repo.py <repo-url>

The script reads the token from `.env`, calls the GitHub API recursively, and prints a tree of files and folders.

### When to use file mode

When the user asks to see the **content** of a specific file, or wants to **read** a specific file in a repository.

Run:

    python fetch_repo.py <repo-url> --file <path>

Where `<path>` is the path relative to the repository root (e.g. `README.md`, `planner/main.py`).

The script fetches the file, decodes it from Base64, and prints its UTF-8 content.

### Choosing the right mode

- User says "show structure" or "list files" → **tree mode**
- User says "show README" or "read planner/main.py" → **file mode**
- User says "analyze this repo" without more detail → start with **tree mode**, then optionally offer to read specific files

## Combining modes

Both modes can be used in sequence to explore a repository:

1. First, run tree mode to see the overall structure
2. Identify interesting files (e.g. `README.md`, entry points, config files)
3. Read them individually with file mode

This is especially useful when generating repository reports or explaining a codebase.

## Important rules

- **Do not re-implement the API call yourself.** Always call `fetch_repo.py` — it handles authentication, error messages, and base64 decoding.
- **Do not modify `fetch_repo.py`** as part of using this skill. If the script has a bug, report it to the user instead of working around it.
- **Do not print the `GITHUB_TOKEN`** or its value anywhere in output, even for debugging.

## Error handling

The helper script prints clear error messages for the common failure cases:

- **Authentication failed** — token missing or invalid. Ask the user to check `.env`.
- **Rate limit exceeded** — GitHub API limit reached. Ask the user to try again later.
- **Not found: file X** or **Not found: owner/repo** — the resource doesn't exist or the URL is malformed.
- **Path is not a file (it's a directory)** — user tried file mode on a directory path. Suggest they either use tree mode, or specify a file inside the directory.
- **Cannot decode file as UTF-8 (likely binary)** — the file is binary (image, compiled code, etc.). Cannot be read as text.

If the script exits with a non-zero code, surface the error message to the user verbatim and do not proceed.

## Examples

**User:** "Analyze github.com/Wins-s/task-ai-mind"

**Action:** Run `python fetch_repo.py https://github.com/Wins-s/task-ai-mind` and show the tree.

**User:** "Show me the README of github.com/psf/requests"

**Action:** Run `python fetch_repo.py https://github.com/psf/requests --file README.md` and show the content.

**User:** "What does planner/main.py do in Wins-s/task-ai-mind?"

**Action:**
1. Run `python fetch_repo.py https://github.com/Wins-s/task-ai-mind --file planner/main.py`
2. Read the printed content
3. Explain what the file does based on the code