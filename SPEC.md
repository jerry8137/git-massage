# git-massage
1. Overview
git-massage is a Python-based CLI tool that generates semantic Git commit messages from staged changes using the OpenAI API.

It differentiates itself from other tools by treating the Edit Loop as a first-class citizen—users are expected to review and "massage" the AI's output in their preferred editor before committing. It is built on a modern Python stack (uv, typer, rich) and is designed to be easily integrated into Neovim workflows.

2. Goals & Principles
The "Massage" Philosophy: AI gets you 80% of the way there; the user perfects the last 20%. The tool must facilitate easy editing.

Editor Agnostic: Works seamlessly with $EDITOR (Vim, Neovim, Nano, VS Code).

Integration Ready: Must support a "pipe mode" (stdout only) for integration with Neovim plugins or other automation tools.

Convention Compliant: Strictly enforces Conventional Commits (e.g., feat:, fix:).

Modern Stack: Built using uv for package management and Typer for the CLI.

3. Architecture
3.1. Tech Stack
Language: Python 3.12+

Project Manager: uv (standard app layout).

CLI Framework: Typer (Interface) + Rich (Spinners/Tables).

AI Client: openai (Official Python SDK).

Git Interaction: subprocess (calling git binary directly).

3.2. Directory Structure
Plaintext

git-massage/
├── pyproject.toml       # Dependencies (typer, rich, openai, tomli-w)
├── README.md
├── src/
    └── git_massage/
        ├── __init__.py
        ├── main.py      # CLI Entry point
        ├── git.py       # Git wrapper (diffs, commits)
        ├── ai.py        # OpenAI interaction
        ├── config.py    # Config loader (TOML + Env)
        └── utils.py     # Formatting helpers
4. Functional Requirements
4.1. Configuration
The tool loads config from ~/.config/git-massage/config.toml (XDG compliant). Fields:

api_key: String (Required).

model: String (Default: gpt-4o).

prompt_style: String (Default: "concise").

exclude_files: List[String] (Default: ["*-lock.json", "*.lock", "go.sum", "*.svg"]).

4.2. Git Integration
Staged Changes Only: The tool must run git diff --cached to see only what will be committed.

Noise Filtering: Before sending the diff to the AI, filter out:

Files matching exclude_files (lockfiles are noise).

Deleted files (send only the filename, not the diff content).

Binary files.

4.3. Modes of Operation
Mode A: Interactive (Default)
Analyze: Read staged diff.

Generate: Call OpenAI with a spinner ("Thinking...").

Preview: Display the generated message in a formatted box.

Action Menu:

[c]ommit: Execute git commit -m "...".

[e]dit: Open the message in $EDITOR (temp file). When the editor closes, read the file back and update the message.

[r]egenerate: Re-run the prompt (optionally ask user for a "hint" e.g., "Focus on the API change").

[q]uit: Exit without committing.

Mode B: Pipe/Raw (--print-only)
Purpose: For Neovim/Plugin integration.

Behavior:

Read staged diff.

Generate message.

Print only the raw message to stdout.

Exit with code 0.

Crucial: No spinners, no logs, no ANSI colors in stdout. All logs must go to stderr.

4.4. AI Prompt Engineering
System Prompt:

You are an expert developer. Generate a commit message following Conventional Commits. Format: <type>(<scope>): <subject> followed by a blank line and a bulleted body if necessary.

Types: feat, fix, docs, style, refactor, test, chore.

Subject: Imperative mood, max 72 chars.

Body: Explain what and why, not just how.

IMPORTANT: Return strictly the message. No markdown blocks (```).

5. Implementation Plan
Phase 1: Core & Git
Initialize with uv init --app.

Implement git.py: get_staged_diff(), commit(msg).

Implement Git noise filtering (strip lockfiles from the diff string).

Phase 2: AI & Config
Implement config.py using tomli/tomllib.

Implement ai.py:

Handle OpenAIError gracefully.

Implement the prompt logic.

Phase 3: The Interactive CLI
Build main.py with Typer.

Implement the Edit Loop:

Use typer.edit() or subprocess.call([editor, temp_file]).

This is the critical "Massage" feature. Ensure the user can edit, save, and then the tool confirms the new message before committing.

Phase 4: Neovim Support (--print-only)
Add a flag git-massage --print-only.

Ensure rich.console is configured to write to stderr when this flag is active, so stdout remains pure text.

6. Neovim Integration Guide (For README)
Add this section to the generated README so users know how to use it.

Option 1: Floating Terminal Use toggleterm.nvim or similar to run git-massage in a popup window.

Lua

-- Lua config example
vim.keymap.set('n', '<leader>gm', '<cmd>TermExec cmd="git-massage"<CR>')
Option 2: Native Buffer Integration Use the --print-only flag to insert the message into your current buffer (e.g., inside a fugitive window or a blank commit buffer).

Lua

vim.api.nvim_create_user_command('GitMassage', function()
  local handle = io.popen("git-massage --print-only")
  local result = handle:read("*a")
  handle:close()
  -- Insert result at cursor
  vim.api.nvim_put(vim.split(result, "\n"), 'c', true, true)
end, {})
7. Success Criteria
Running git-massage on a repository with staged changes opens a TUI.

The generated message follows feat: ... format.

Pressing e opens Vim/Nano, user changes text, saves, and the tool captures the edit.

Running git-massage --print-only > msg.txt creates a file containing only the commit message, no logs.
