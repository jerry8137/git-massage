from rich.console import Console
from rich.theme import Theme

custom_theme = Theme(
    {
        "info": "dim cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
    }
)

console = Console(theme=custom_theme)


def print_error(message: str) -> None:
    console.print(f"[error]Error:[/error] {message}")


def print_success(message: str) -> None:
    console.print(f"[success]{message}[/success]")


def print_info(message: str) -> None:
    console.print(f"[info]{message}[/info]")
