"""Fetch GitHub repository structure or file contents via API.

Usage:
    # Print recursive file tree (default mode)
    python fetch_repo.py <github_repo_url>

    # Print content of a specific file
    python fetch_repo.py <github_repo_url> --file <path>

Examples:
    python fetch_repo.py https://github.com/Wins-s/task-ai-mind
    python fetch_repo.py https://github.com/Wins-s/task-ai-mind --file README.md
    python fetch_repo.py https://github.com/Wins-s/task-ai-mind --file planner/main.py

Requires GITHUB_TOKEN in .env file.
"""

import argparse
import base64
import os
import sys

# Force UTF-8 output on Windows for emoji support
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

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


def _github_get(path: str, token: str) -> requests.Response:
    """Perform an authenticated GET request to the GitHub API.

    Returns the raw response object. Callers are responsible for interpreting it.
    """
    url = f"{GITHUB_API_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    return requests.get(url, headers=headers)


def _check_response(response: requests.Response, resource_hint: str) -> None:
    """Raise a RuntimeError with a human-readable message for common failures."""
    if response.status_code == 200:
        return
    if response.status_code == 401:
        raise RuntimeError("Authentication failed. Check your GITHUB_TOKEN.")
    if response.status_code == 403:
        raise RuntimeError("Rate limit exceeded or access forbidden.")
    if response.status_code == 404:
        raise RuntimeError(f"Not found: {resource_hint}")
    raise RuntimeError(f"API error: {response.status_code} — {response.text}")


def fetch_contents(owner: str, repo: str, path: str, token: str) -> list[dict]:
    """Fetch the contents of a directory in a GitHub repo.

    Returns a list of items (files and subdirectories).
    """
    response = _github_get(f"/repos/{owner}/{repo}/contents/{path}", token)
    _check_response(response, f"{owner}/{repo}/{path}")
    return response.json()


def fetch_file_content(owner: str, repo: str, path: str, token: str) -> str:
    """Fetch and decode the content of a single file in a GitHub repo.

    Returns the file content as UTF-8 text.
    Raises RuntimeError if the path is not a file or content is not UTF-8.
    """
    response = _github_get(f"/repos/{owner}/{repo}/contents/{path}", token)
    _check_response(response, f"file {path}")

    data = response.json()

    # If GitHub returns a list, the path points to a directory, not a file
    if isinstance(data, list):
        raise RuntimeError(f"Path is not a file (it's a directory): {path}")

    if data.get("type") != "file":
        raise RuntimeError(
            f"Path is not a file: {path} (type: {data.get('type')})"
        )

    encoded = data.get("content", "")
    encoding = data.get("encoding", "base64")

    if encoding != "base64":
        raise RuntimeError(f"Unsupported encoding: {encoding}")

    try:
        decoded_bytes = base64.b64decode(encoded)
        return decoded_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise RuntimeError(
            f"Cannot decode file as UTF-8 (likely binary): {path}"
        )


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


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="fetch_repo",
        description="Fetch GitHub repository structure or file contents via API.",
    )
    parser.add_argument("repo_url", help="GitHub repository URL")
    parser.add_argument(
        "--file",
        metavar="PATH",
        help="Fetch content of a specific file (path relative to repo root)",
    )
    return parser


def main() -> int:
    """Entry point for the script."""
    parser = build_parser()
    args = parser.parse_args()

    load_dotenv()
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        print("Error: GITHUB_TOKEN not found in .env file", file=sys.stderr)
        return 1

    try:
        owner, repo = parse_repo_url(args.repo_url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        if args.file:
            content = fetch_file_content(owner, repo, args.file, token)
            print(content)
        else:
            print(f"Repository: {owner}/{repo}\n")
            print_tree(owner, repo, "", token)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())