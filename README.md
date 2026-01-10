# git-massage

Automate semantic git commit messages using OpenAI. `git-massage` analyzes your staged changes and generates high-quality, convention-compliant commit messages, saving you time and ensuring a clean git history.

## Demo

![demo video](https://github.com/jerry8137/git-massage/raw/master/assets/demo.gif "Demo")

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

### --print-only Mode (Editor Integration)

For seamless integration with editors like Neovim, use the `--print-only` flag. This mode:
- Prints only the raw commit message to stdout
- Redirects all logs and spinners to stderr
- Exits immediately after generation (no interactive prompt)

```bash
# Capture message to a file
uv run git-massage --print-only > commit_message.txt

# Use in a pipeline
git commit -m "$(uv run git-massage --print-only)"
```

## Neovim Integration

### Option 1: Floating Terminal (Interactive Mode)

Use a terminal plugin like [toggleterm.nvim](https://github.com/akinsho/toggleterm.nvim) to run the full interactive experience:

```lua
-- In your Neovim config (e.g., ~/.config/nvim/lua/config/keymaps.lua)
vim.keymap.set('n', '<leader>gm', '<cmd>TermExec cmd="git-massage"<CR>', {
    desc = "Generate commit message with git-massage"
})
```

### Option 2: Direct Buffer Insertion (--print-only)

Insert the generated message directly into your current buffer:

```lua
-- In your Neovim config
vim.api.nvim_create_user_command('GitMassage', function()
  -- Generate message using --print-only mode
  local handle = io.popen("git-massage --print-only 2>/dev/null")
  local result = handle:read("*a")
  handle:close()

  -- Insert at cursor position
  if result and result ~= "" then
    vim.api.nvim_put(vim.split(result, "\n"), 'c', true, true)
  else
    vim.notify("Failed to generate commit message", vim.log.levels.ERROR)
  end
end, {})

-- Bind to a key
vim.keymap.set('n', '<leader>gc', '<cmd>GitMassage<CR>', {
    desc = "Insert git-massage commit message"
})
```

### Option 3: Git Commit Integration

Automatically populate Git commit messages in fugitive or vim-fugitive buffers:

```lua
-- Auto-populate commit message in git commit buffers
vim.api.nvim_create_autocmd("FileType", {
    pattern = "gitcommit",
    callback = function()
        vim.keymap.set('n', '<leader>gm', function()
            vim.cmd('0read !git-massage --print-only 2>/dev/null')
        end, { buffer = true, desc = "Generate commit message" })
    end,
})
```

## Configuration
Configuration is stored in `~/.config/git-massage/config.toml`.

```toml
openai_api_key = "sk-..."
model = "gpt-4o"
max_diff_lines = 500
exclude_files = ["*-lock.json", "*.lock", "go.sum", "*.svg"]
```

**Available Options:**
- `openai_api_key`: Your OpenAI API key (can also use `OPENAI_API_KEY` env var)
- `model`: OpenAI model to use (default: "gpt-4o")
- `max_diff_lines`: Maximum lines of diff to send to AI
- `exclude_files`: Glob patterns for files to exclude from diff (reduces noise and saves tokens)

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
