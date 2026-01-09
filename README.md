# git-massage

Automate semantic git commit messages using OpenAI. `git-massage` analyzes your staged changes and generates high-quality, convention-compliant commit messages, saving you time and ensuring a clean git history.

## Features

- **Zero-Friction**: Automatically runs `git diff --cached` to analyze staged changes.
- **Conventional Commits**: Generates messages in `<type>(<scope>): <subject>` format (e.g., `feat(auth): add login endpoint`).
- **Interactive Workflow**:
  - **Commit**: Accept the generated message immediately.
  - **Edit**: Refine the message in your default editor (`$EDITOR`).
  - **Regenerate**: Ask AI to try again if the first attempt isn't perfect.
- **Smart Context**: Automatically excludes lockfiles (`package-lock.json`, `uv.lock`, etc.) to save tokens and reduce noise.
- **Configurable**: Persists settings like API keys and model preferences in `~/.config/git-massage/config.toml`.

## Installation

### Prerequisites
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended)

### From Source
```bash
# Clone the repository
git clone https://github.com/yourusername/git-massage.git
cd git-massage

# Install dependencies
uv sync

# Run via uv
uv run git-massage --help
```

## Usage

### 1. Setup
First, configure your OpenAI API key. This will be saved to `~/.config/git-massage/config.toml`.

```bash
uv run git-massage setup
```
*Alternatively, you can set the `OPENAI_API_KEY` environment variable.*

### 2. Generate Commit Message
Stage your changes as usual, then run the tool:

```bash
git add .
uv run git-massage
```

The tool will:
1. Analyze your staged changes.
2. Display a generated commit message.
3. Prompt for action:
   - `[c]ommit`: Execute `git commit` with the message.
   - `[e]dit`: Open the message in your editor for manual tweaks.
   - `[r]egenerate`: Request a new message from the AI.
   - `[q]uit`: Exit without doing anything.

### Options
You can override configuration defaults via CLI flags:

```bash
# Use a specific model
uv run git-massage --model gpt-4-turbo

# Pass API key directly
uv run git-massage --api-key sk-...
```

## Configuration
Configuration is stored in `~/.config/git-massage/config.toml`.

```toml
openai_api_key = "sk-..."
model = "gpt-4o"
max_diff_lines = 500
```

## Development

This project uses `uv` for dependency management and `ruff` for linting.

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format .
```

## License
[MIT](LICENSE)
