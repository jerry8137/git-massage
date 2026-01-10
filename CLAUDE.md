# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview
`git-massage` is a Python CLI tool that generates semantic git commit messages using OpenAI's API. It analyzes staged changes and creates Conventional Commits-compliant messages with an interactive workflow for committing, editing, or regenerating messages.

## Development Commands

### Package Management (uv)
This project uses `uv` exclusively - do NOT use pip or poetry.

```bash
# Install/sync all dependencies
uv sync

# Add a runtime dependency
uv add <package_name>

# Add a dev dependency
uv add --dev <package_name>

# Run the application
uv run git-massage
uv run python main.py  # alternative

# Run with options
uv run git-massage --setup
uv run git-massage --model gpt-4-turbo

# Run in --print-only mode (for Neovim/editor integration)
uv run git-massage --print-only > message.txt
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_smoke.py

# Run specific test function
uv run pytest tests/test_smoke.py::test_imports

# Verbose output
uv run pytest -v
```

### Linting & Formatting
```bash
# Check code quality
uv run ruff check .

# Auto-fix lint issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

## Architecture

### Module Organization
The codebase follows a clean separation of concerns across 5 core modules in `src/git_massage/`:

1. **main.py** - Entry point and CLI orchestration
   - Typer app definition with default callback (`default_command()`) and `setup` subcommand
   - Default behavior: runs commit message generation when no subcommand specified
   - Interactive loop handling user choices: [c]ommit, [e]dit, [r]egenerate, [q]uit
   - `--print-only` flag for editor integration (Neovim) - outputs pure message to stdout
   - Regenerate hint support: prompts for optional guidance when regenerating
   - Coordinates calls to config, git, and ai modules
   - Handles CLI argument overrides for model and API key

2. **git.py** - Git subprocess wrapper
   - `get_staged_diff(exclude_files)` - Retrieves `git diff --cached` with exclusions
   - `_filter_diff_noise(diff)` - Filters binary files and deleted files to reduce noise
   - `commit(message)` - Executes `git commit -m`
   - Uses subprocess directly (no GitPython dependency)
   - Raises `GitError` on failures
   - **Noise filtering**: Binary files show only "Binary files differ", deleted files show only filename

3. **ai.py** - OpenAI API integration
   - `generate_message(diff, model, api_key, hint=None)` - Calls OpenAI Chat Completions API
   - Optional `hint` parameter for regenerate guidance (e.g., "focus on security")
   - Contains `SYSTEM_PROMPT` enforcing Conventional Commits format
   - Temperature set to 1 for variety
   - Handles OpenAI-specific errors (AuthenticationError)

4. **config.py** - Configuration management
   - Loads from `~/.config/git-massage/config.toml` (TOML format)
   - Precedence: CLI args → env vars → config file → defaults
   - `load_config()` - Merges all config sources
   - `save_config(key, value)` - Persists to TOML file
   - Environment variables: `OPENAI_API_KEY`, `GIT_MASSAGE_MODEL`
   - **DEFAULT_CONFIG includes**: model (gpt-4o), max_diff_lines (500), exclude_files (lockfiles, SVGs)

5. **utils.py** - UI helpers
   - Rich console with custom theme (error/success/info/warning styles)
   - Helper functions: `print_error()`, `print_success()`, `print_info()`
   - **--print-only mode support**:
     - `console_stderr` - Console that writes to stderr for clean stdout
     - `set_print_only_mode(enabled)` - Global mode switch
     - `get_console()` - Returns appropriate console based on mode

### Data Flow
```
User runs `uv run git-massage`
    ↓
main.py loads config (config.py)
    ↓
git.py retrieves staged diff (excludes lockfiles)
    ↓
main.py truncates diff to 4000 chars if needed
    ↓
ai.py sends diff to OpenAI with SYSTEM_PROMPT
    ↓
main.py displays message with Rich formatting
    ↓
Interactive loop: user chooses action
    ↓
[commit] → git.py executes git commit
[edit] → typer.edit() opens $EDITOR → loop continues
[regenerate] → ai.py called again
[quit] → exit
```

### Key Design Decisions
- **No heavy Git dependencies**: Uses subprocess for git commands to stay lightweight
- **Configurable exclusions**: `exclude_files` in config.toml with patterns like `*-lock.json`, `*.lock`, `go.sum`, `*.svg` (defaults provided)
- **Noise filtering**: Binary files and deleted files automatically filtered to reduce diff noise
- **Diff truncation**: Limits diffs to 4000 characters to avoid token limits
- **Config persistence**: Stores settings in XDG-compliant location (`~/.config/git-massage/`)
- **Interactive workflow**: Always requires user confirmation before committing
- **--print-only mode**: Stdout/stderr separation for Neovim integration - only commit message to stdout, all UI to stderr
- **Regenerate hints**: Optional user guidance when regenerating (e.g., "focus on security improvements")

## Code Style

### Type Hints (MANDATORY)
All functions must have type hints for arguments and return values:
```python
def calculate_sum(a: int, b: int) -> int:
    return a + b
```

### Naming Conventions
- Variables/Functions: `snake_case` (e.g., `get_staged_diff`)
- Classes: `PascalCase` (e.g., `GitError`)
- Constants: `UPPER_CASE` (e.g., `SYSTEM_PROMPT`, `DEFAULT_CONFIG`)
- Private members: prefix with `_` (e.g., `_run_git_command`)

### Imports
- Use absolute imports: `from git_massage.utils import console`
- Group: standard library → third-party → local
- Remove unused imports (ruff will flag these)

### Error Handling
- Use specific exceptions over generic `Exception`
- Module-specific errors: `GitError` in git.py
- Handle `typer.Exit` for CLI termination
- Use `rich.console` for user-facing messages, NOT `print()`

## Conventional Commits
This project enforces Conventional Commits format both for AI-generated messages and repository commits:
- Format: `<type>(<optional-scope>): <subject>`
- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`
- Use imperative mood ("add" not "added")
- First line max 72 characters
- Optional bulleted body for significant changes

## Configuration Reference
Located at `~/.config/git-massage/config.toml`:
```toml
openai_api_key = "sk-..."
model = "gpt-4o"
max_diff_lines = 500
exclude_files = ["*-lock.json", "*.lock", "go.sum", "*.svg"]
```

**Configuration Options:**
- `openai_api_key` - OpenAI API key (can also use OPENAI_API_KEY env var)
- `model` - OpenAI model (default: "gpt-4o")
- `max_diff_lines` - Maximum diff lines (default: 500)
- `exclude_files` - Glob patterns to exclude from diffs (default: lockfiles and SVGs)

**--print-only Flag:**
Use `git-massage --print-only` for Neovim/editor integration. Outputs only the commit message to stdout with all logs going to stderr.
