from rich.console import Console
from rich.theme import Theme
import sys

custom_theme = Theme(
    {
        "info": "dim cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
    }
)

# Default console writes to stdout (for interactive mode)
console = Console(theme=custom_theme)

# Stderr console for --print-only mode (keeps stdout clean)
console_stderr = Console(theme=custom_theme, file=sys.stderr)

# Global flag to control which console is active
_print_only_mode = False


def set_print_only_mode(enabled: bool) -> None:
    """Enable --print-only mode, which redirects all Rich output to stderr."""
    global _print_only_mode
    _print_only_mode = enabled


def get_console() -> Console:
    """Return stderr console in --print-only mode, stdout console otherwise."""
    return console_stderr if _print_only_mode else console


def print_error(message: str) -> None:
    get_console().print(f"[error]Error:[/error] {message}")


def print_success(message: str) -> None:
    get_console().print(f"[success]{message}[/success]")


def print_info(message: str) -> None:
    get_console().print(f"[info]{message}[/info]")
