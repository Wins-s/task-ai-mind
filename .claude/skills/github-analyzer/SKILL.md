---
name: github-analyzer
description: Analyzes the structure of a GitHub repository via the GitHub REST API. Fetches the recursive file and folder tree of any accessible repository and displays it in the console. Triggers on requests to inspect, describe, list files, show structure, or analyze a GitHub repository — e.g. "show me the structure of github.com/user/repo", "list files in this GitHub repo", "what's in <repo-url>", "analyze https://github.com/...".
allowed-tools: Bash(python:*), Bash(python3:*)
---

# GitHub Repository Analyzer

This skill inspects the structure of a GitHub repository through the GitHub REST API and prints the file tree to the console.

## Prerequisites

- A `GITHUB_TOKEN` environment variable must be present in the project's `.env` file. The token is a GitHub fine-grained Personal Access Token with `Contents: Read-only` permission on the target repository.
- The helper script `fetch_repo.py` must exist in the project root.
- Python dependencies (`requests`, `python-dotenv`) must be installed — they are listed in `requirements.txt`.

## Workflow

When the user asks to analyze, inspect, or list the contents of a GitHub repository:

1. **Identify the repository URL** in the user's message. Accept forms like:
   - `https://github.com/owner/repo`
   - `github.com/owner/repo`
   - `owner/repo` (assume GitHub)

2. **Run the helper script** with the URL as a single argument:

       python fetch_repo.py <repo-url>

   The script reads the token from `.env`, calls the GitHub API recursively, and prints a tree of files and folders.

3. **Do not re-implement the API call yourself.** Always call `fetch_repo.py` — it already handles authentication, pagination, error messages, and formatting.

4. **Present the output** to the user. If the tree is long, summarize the top-level structure and offer to drill deeper on request.

## Error handling

The helper script prints clear error messages for the common failure cases:

- **Authentication failed** — token missing or invalid. Ask the user to check `.env`.
- **Rate limit exceeded** — GitHub API limit reached. Ask the user to try again later.
- **Repository not found** — either the repo doesn't exist, is private without token access, or the URL is malformed.
- **Invalid GitHub repo URL** — the URL couldn't be parsed. Ask the user to provide a correct one.

If the script exits with a non-zero code, surface the error message to the user verbatim and do not proceed with further analysis.

## Examples

**User:** "Analyze github.com/Wins-s/task-ai-mind"

**Action:** Run `python fetch_repo.py https://github.com/Wins-s/task-ai-mind` and show the tree.

**User:** "What files are in https://github.com/psf/requests?"

**Action:** Run `python fetch_repo.py https://github.com/psf/requests` and summarize the top-level structure.