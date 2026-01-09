# git-massage
1. Overview
git-massage is a command-line interface (CLI) tool written in Python. It automates the generation of high-quality, convention-compliant Git commit messages by analyzing staged changes in a repository. It leverages the OpenAI API to summarize code changes and enforces the Conventional Commits specification.

2. Goals & Principles
Zero-Friction: The tool must be faster and easier than writing a commit message manually.

Convention Compliant: Strictly adhere to Conventional Commits (e.g., feat:, fix:, chore:) by default.

Modern Stack: Built using uv for package/project management and Typer for the CLI interface.

Privacy-First: User must explicitly confirm the message before committing. Large diffs or sensitive files (lockfiles) should be truncated or excluded.

3. User Stories
As a developer, I want to run git-massage and have it automatically detect my staged changes so I don't have to copy-paste diffs.

As a developer, I want the generated message to follow the format <type>(<scope>): <subject> with an optional body, so my git history remains clean.

As a developer, I want to edit the generated message before finalizing the commit in case the AI missed a detail.

As a developer, I need to configure my OpenAI API key once and have it persist across sessions.

As a developer, I want to customize the "focus" (e.g., "be funny", "be professional", "focus on performance") via a configuration flag or file.

4. Technical Architecture
4.1. Tech Stack
Language: Python 3.12+

Package Manager: uv (for dependency resolution and environment management).

CLI Framework: Typer (with Rich for pretty terminal output).

Git Interface: subprocess (calling native git commands directly to avoid heavy dependencies like GitPython).

AI Provider: OpenAI API (Client openai).

4.2. Project Structure
The project should follow the standard uv application layout:

Plaintext

git-massage/
├── pyproject.toml       # Dependencies and tool configuration
├── README.md
├── .gitignore
├── .env                 # Local secrets (not committed)
└── src/
    └── git_massage/
        ├── __init__.py
        ├── main.py      # Entry point (Typer app)
        ├── git.py       # Git subprocess wrappers
        ├── ai.py        # OpenAI API interaction logic
        ├── config.py    # Configuration management
        └── utils.py     # Helper functions (logging, formatting)
5. Functional Requirements
5.1. Configuration Management
The tool must look for configuration in the following order of precedence:

Command Line Args (e.g., --api-key, --model).

Environment Variables (OPENAI_API_KEY, GIT_MASSAGE_MODEL).

Config File (~/.config/git-massage/config.toml or XDG compliant path).

Required Config:

openai_api_key: String (Required)

model: String (Default: gpt-4o, Fallback: gpt-3.5-turbo)

max_diff_lines: Integer (Default: 500 to save tokens)

5.2. Git Integration
Check Staged Changes: Run git diff --cached to retrieve the diff.

Edge Case: If no changes are staged, exit with a helpful error message: "No staged changes found. Did you run 'git add'?"

Exclude Lockfiles: Automatically exclude package-lock.json, uv.lock, poetry.lock, yarn.lock, and go.sum from the diff context sent to the AI to prevent token waste.

5.3. AI Prompt Engineering
The prompt sent to OpenAI must be structured to ensure valid JSON or strict text output.

System Prompt:

You are a helpful assistant that writes semantic Git commit messages. You must output the message following the Conventional Commits specification. Format: <type>(<optional-scope>): <subject> Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert. Rules:

Use imperative mood ("add" not "added").

First line max 72 characters.

If the changes are significant, add a bulleted body description.

Do not output markdown code blocks (```). Just the raw message.

5.4. CLI Workflow
Init: User runs git-massage.

Validation: Tool checks for API Key. If missing, prompts user to enter it and saves it to ~/.config/git-massage/config.toml.

Analysis: Tool reads staged git diff.

Thinking: Show a spinner (via rich.console) while waiting for API response.

Review:

Display the generated message.

Options: [c]ommit, [e]dit, [r]egenerate, [q]uit.

Action:

Commit: Runs git commit -m "...".

Edit: Opens the message in the user's $EDITOR (or vim/nano fallback).

Regenerate: Resends request to OpenAI (optional: allow user to provide a hint like "focus on the API change").

6. Implementation Steps
Phase 1: Setup
Initialize project: uv init --app --package git-massage.

Add dependencies: uv add typer[all] openai rich tomli-w (and tomli if python < 3.11).

Create the directory structure.

Phase 2: Core Logic
Implement git.py: Functions to get_staged_diff() and commit(message).

Implement config.py: Logic to load/save TOML config and handle env vars.

Implement ai.py: Function generate_message(diff, model) that calls OpenAI.

Phase 3: The CLI
Build main.py using Typer.

Create the main command.

Add the interactive loop (Commit/Edit/Regenerate).

Phase 4: Polish
Add specific handling for AuthenticationError (OpenAI) and GitCommandError.

Implement the "Edit" functionality using typer.edit().

Add a --setup command to easily configure keys.

7. Example Usage
Bash

# 1. Normal usage (uses env var or config file)
$ git add .
$ git-massage

# 2. First time setup
$ git-massage --setup

# 3. Override model
$ git-massage --model gpt-4-turbo
8. Safety & Limits
Token Limit: If the diff exceeds 4000 characters, truncate it and append a note to the system prompt: "[Diff truncated]".

Secrets: Do not attempt to scrub secrets (too complex for MVP), but warn the user in the README that staged code is sent to OpenAI.

9. Future Improvements (Post-MVP)
Support for git hook installation (prepare-commit-msg).

Support for local LLMs (Ollama) via a --provider flag.

Custom system prompts per repository (reading from .git-massage in repo root).
