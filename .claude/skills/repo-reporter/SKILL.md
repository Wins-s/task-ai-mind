---
name: repo-reporter
description: Generates a comprehensive technical report about any accessible GitHub repository and saves it as Markdown. The report covers project overview, tech stack, structure, strengths, areas for improvement, and actionable recommendations. Triggers on requests like "generate a report about github.com/user/repo", "analyze this repository and write a report", "give me a technical review of <repo-url>", "create a project report for <repo-url>", "summarize what's in <repo-url>".
allowed-tools: Bash(python:*), Bash(python3:*), Bash(mkdir:*), Read, Write, SlashCommand(github-analyzer)
---

# GitHub Repository Reporter

This skill produces a comprehensive technical report about a GitHub repository. It orchestrates the `github-analyzer` skill to gather context, then synthesizes findings into a structured Markdown document saved under `output/`.

## Prerequisites

- The `github-analyzer` skill must be available in this project (it should be at `.claude/skills/github-analyzer/`).
- All prerequisites of `github-analyzer` apply here as well (`GITHUB_TOKEN` in `.env`, Python dependencies installed).
- The `output/` directory will be created automatically if it does not exist.

## Workflow

### Step 1 — Fetch the repository tree

Call `github-analyzer` in tree mode to get the full file/folder structure:

    python fetch_repo.py <repo-url>

Study the output. Identify:
- Programming language(s) used (from file extensions)
- Presence of standard project files (README, LICENSE, config files)
- Overall depth and complexity of the structure
- Framework or tool signatures (`package.json` → Node.js, `requirements.txt` → Python, `Cargo.toml` → Rust, `pom.xml` → Java Maven, `go.mod` → Go, etc.)

### Step 2 — Read key files for context

Based on the tree, select a small set of files that carry the most signal. Prioritize (in this order):

1. **`README.md`** or **`README`** — always read this if present
2. **Dependency manifests** — `requirements.txt`, `pyproject.toml`, `package.json`, `Cargo.toml`, `pom.xml`, `go.mod`, `Gemfile`
3. **Entry points** — `main.py`, `__main__.py`, `index.js`, `main.go`, `Program.cs`, `src/main/*`
4. **Configuration files** if present — `Dockerfile`, `.github/workflows/*.yml`, `Makefile`
5. **A couple of core source files** that appear central to the project

Read each with:

    python fetch_repo.py <repo-url> --file <path>

**Do not read every file.** Cap the total at around 5–8 files to keep the analysis focused and the token usage reasonable.

### Step 3 — Synthesize the analysis

Combine the tree structure and file contents to form your understanding of the project. Then compose a Markdown report following the exact template in the next section.

The report must be:
- **Factual** — do not invent features, technologies, or issues that are not observable from the code
- **Constructive** — suggestions should be actionable and prioritized
- **Concise** — one screen per section is a good target; avoid filler

### Step 4 — Save the report

Ensure `output/` exists (create it if not), then write the report to `output/report.md`.

If a previous `output/report.md` already exists, overwrite it (the report always reflects the latest analysis).

### Step 5 — Notify the user

After saving, tell the user:
- Where the report was saved
- A very brief 2–3 sentence summary of the main findings

Do not paste the full report in the chat — the file is the deliverable.

## Report template

Save the following structure into `output/report.md`, filling in each section from your analysis:

    # Technical Report: <owner>/<repo>

    **Generated:** <YYYY-MM-DD>
    **Source:** <full repo URL>

    ## Overview

    A 2–4 sentence description of what the project does, its intended audience,
    and its current state (early stage / stable / archived, etc.).

    ## Tech Stack

    - **Language(s):** <e.g. Python 3.13>
    - **Frameworks / libraries:** <e.g. FastAPI, SQLAlchemy>
    - **Build / packaging:** <e.g. pip + requirements.txt, poetry, setuptools>
    - **Runtime / deployment hints:** <e.g. Dockerfile present, GitHub Actions CI>
    - **Notable dev tooling:** <e.g. pytest, ruff, mypy>

    ## Structure

    A short description of how the code is organized. Mention the top-level
    folders and what each one is responsible for. Highlight any unusual or
    interesting architectural choices.

    ## Strengths

    A bulleted list of what the project does well. Keep each point one line
    and grounded in what you actually saw in the code / files.

    ## Areas for Improvement

    A bulleted list of concrete issues, gaps, or risks. Avoid vague criticism;
    every item should point at something observable.

    ## Recommendations

    A numbered list of prioritized, actionable suggestions. Each recommendation
    should say **what** to do and **why** it would help. Keep the list short
    (3–6 items) and focus on high-impact changes.

    ---
    *Report generated automatically via the `repo-reporter` skill.*

## Important rules

- **Delegate all API calls to `github-analyzer`.** Do not call the GitHub API directly from within this skill.
- **Do not invent files or content.** If you did not read a file, do not describe its contents.
- **Do not include the `GITHUB_TOKEN`** or any secrets in the report or anywhere in output.
- **Do not push, commit, or modify Git state** as part of this skill. The report is a working artifact; committing is the user's decision.
- **If a step fails**, stop, surface the error to the user verbatim, and do not proceed with the report.

## Examples

**User:** "Generate a report about github.com/Wins-s/task-ai-mind"

**Action:**
1. Run `python fetch_repo.py https://github.com/Wins-s/task-ai-mind`
2. Read `README.md`, `requirements.txt`, `planner/main.py`, `planner/commands.py`, `fetch_repo.py`
3. Synthesize the six-section report using the template above
4. Ensure `output/` exists (`mkdir -p output`), save to `output/report.md`
5. Confirm to the user with a 2–3 sentence summary

**User:** "Analyze https://github.com/psf/requests and give me a technical review"

**Action:** Same workflow. Report is saved to `output/report.md`, overwriting any previous one.

**User:** "Summarize what's in github.com/octocat/Hello-World"

**Action:** Same workflow, though for such a minimal repo the report will be short. Do not pad it with speculation.