"""Fetch and display GitHub repository file tree via API.

Usage:
    python fetch_repo.py <github_repo_url>

Example:
    python fetch_repo.py https://github.com/Wins-s/task-ai-mind

Requires GITHUB_TOKEN in .env file.
"""

import os
import sys
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv


GITHUB_API_BASE = "https://api.github.com"


def parse_repo_url(url: str) -> tuple[str, str]:
    """Extract (owner, repo) from a GitHub repo URL.

    Accepts URLs like:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - github.com/owner/repo
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")

    if len(parts) < 2:
        raise ValueError(f"Invalid GitHub repo URL: {url}")

    owner = parts[0]
    repo = parts[1].removesuffix(".git")

    return owner, repo


def fetch_contents(owner: str, repo: str, path: str, token: str) -> list[dict]:
    """Fetch the contents of a directory in a GitHub repo.

    Returns a list of items (files and subdirectories) from the API.
    Raises an exception on API errors.
    """
    url = f"{GITHUB_API_BASE}/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 401:
        raise RuntimeError("Authentication failed. Check your GITHUB_TOKEN.")
    if response.status_code == 403:
        raise RuntimeError("Rate limit exceeded or access forbidden.")
    if response.status_code == 404:
        raise RuntimeError(f"Repository not found: {owner}/{repo}")
    if response.status_code != 200:
        raise RuntimeError(f"API error: {response.status_code} — {response.text}")

    return response.json()


def print_tree(owner: str, repo: str, path: str, token: str, indent: int = 0) -> None:
    """Recursively print the tree of files and directories."""
    items = fetch_contents(owner, repo, path, token)

    # Sort: directories first, then files, both alphabetically
    items.sort(key=lambda item: (item["type"] != "dir", item["name"]))

    for item in items:
        prefix = "  " * indent
        icon = "📁" if item["type"] == "dir" else "📄"
        print(f"{prefix}{icon} {item['name']}")

        if item["type"] == "dir":
            print_tree(owner, repo, item["path"], token, indent + 1)


def main() -> int:
    """Entry point for the script."""
    if len(sys.argv) != 2:
        print("Usage: python fetch_repo.py <github_repo_url>", file=sys.stderr)
        return 1

    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        print("Error: GITHUB_TOKEN not found in .env file", file=sys.stderr)
        return 1

    try:
        owner, repo = parse_repo_url(sys.argv[1])
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Repository: {owner}/{repo}\n")

    try:
        print_tree(owner, repo, "", token)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())