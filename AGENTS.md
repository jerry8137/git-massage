# AGENTS.md

This file provides context and instructions for AI agents (and humans) working on the `git-massage` repository.

## 1. Project Overview
`git-massage` is a CLI tool to automate semantic git commit messages using OpenAI.
- **Stack**: Python 3.12+, `uv` (package manager), `Typer` (CLI), `Rich` (UI), `OpenAI` (API).
- **Architecture**: Modular design in `src/git_massage/` (see `SPEC.md` for details).

## 2. Environment & Build

### Package Management
This project uses **uv**. Do not use `pip` or `poetry` directly.

- **Install Dependencies**:
  ```bash
  uv sync
  ```
- **Add Dependency**:
  ```bash
  uv add <package_name>
  ```
- **Add Dev Dependency**:
  ```bash
  uv add --dev <package_name>
  ```

### Running the App
- **Run from source**:
  ```bash
  uv run python main.py
  # OR if installed in editable mode
  uv run git-massage
  ```

## 3. Testing & Linting

### Testing (pytest)
*Note: Ensure `pytest` is added as a dev dependency (`uv add --dev pytest`).*

- **Run all tests**:
  ```bash
  uv run pytest
  ```
- **Run a single test file**:
  ```bash
  uv run pytest tests/test_file.py
  ```
- **Run a specific test case**:
  ```bash
  uv run pytest tests/test_file.py::test_function_name
  ```
- **Run with verbose output**:
  ```bash
  uv run pytest -v
  ```

### Linting & Formatting (Ruff)
*Note: Ensure `ruff` is added as a dev dependency (`uv add --dev ruff`).*

- **Check code quality**:
  ```bash
  uv run ruff check .
  ```
- **Fix lint errors**:
  ```bash
  uv run ruff check --fix .
  ```
- **Format code**:
  ```bash
  uv run ruff format .
  ```

## 4. Code Style Guidelines

### Python Conventions
- **Version**: Python 3.12+ features are encouraged.
- **Type Hinting**: **MANDATORY**. All functions and method arguments must have type hints. Return types must be specified.
  ```python
  def calculate_sum(a: int, b: int) -> int:
      return a + b
  ```
- **Imports**:
  - Use absolute imports (e.g., `from git_massage.utils import log`).
  - Group standard library, third-party, and local imports.
  - Remove unused imports.

### Naming
- **Variables/Functions**: `snake_case` (e.g., `get_staged_diff`).
- **Classes**: `PascalCase` (e.g., `GitManager`).
- **Constants**: `UPPER_CASE` (e.g., `DEFAULT_MODEL`).
- **Private members**: Prefix with `_` (e.g., `_api_key`).

### Documentation
- Use concise docstrings for complex functions.
- Comments should explain *why*, not *what*.

### Error Handling
- Use specific exceptions (e.g., `FileNotFoundError`) over generic `Exception`.
- Handle `typer.Exit` for CLI termination.
- Use `rich.console` for user-facing errors, not just `print()`.

## 5. Directory Structure (Target)
Follow the structure defined in `SPEC.md`:
```text
git-massage/
├── pyproject.toml
├── README.md
├── src/
│   └── git_massage/
│       ├── __init__.py
│       ├── main.py      # Typer app entry point
│       ├── git.py       # Git subprocess wrappers
│       ├── ai.py        # OpenAI interactions
│       ├── config.py    # Config loading
│       └── utils.py     # Helpers
└── tests/               # Pytest tests
```

## 6. Development Workflow Rules
1.  **Spec Compliance**: Always refer to `SPEC.md` when implementing features.
2.  **Conventional Commits**: The tool generates them, and we must use them for this repo too.
    - Format: `<type>(<scope>): <subject>`
    - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.
3.  **Secrets**: NEVER commit `.env` or API keys.
4.  **Dependencies**: Always update `pyproject.toml` via `uv add`, never manually edit unless resolving conflicts.

## 7. CLI Interaction (Typer + Rich)
- Use `typer` for command definitions.
- Use `rich` for all output (spinners, tables, colored text).
- Ensure prompts (e.g., "Confirm commit message?") are user-friendly.
