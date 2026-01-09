import typer
from rich.prompt import Prompt
from typing import Optional
from git_massage import config, git, ai
from git_massage.utils import console, print_error, print_success, print_info

app = typer.Typer(
    name="git-massage",
    help="Automate semantic git commit messages using OpenAI.",
    add_completion=False,
)


@app.command()
def setup():
    """
    Configure git-massage (e.g., set API key).
    """
    console.print("[bold]git-massage setup[/bold]")

    api_key = Prompt.ask("Enter your OpenAI API Key", password=True)
    if api_key:
        config.save_config("openai_api_key", api_key)
        print_success("API Key saved to config.")

    model = Prompt.ask("Enter default model", default="gpt-4o")
    config.save_config("model", model)
    print_success(f"Default model set to {model}.")


@app.command()
def main(
    model: Optional[str] = typer.Option(None, help="Override the AI model to use."),
    api_key: Optional[str] = typer.Option(None, help="Override OpenAI API Key."),
    setup_mode: bool = typer.Option(False, "--setup", help="Run setup wizard."),
):
    """
    Generate a commit message from staged changes.
    """
    if setup_mode:
        setup()
        raise typer.Exit()

    cfg = config.load_config()

    # Overrides
    current_model = model or cfg.get("model", "gpt-4o")
    current_api_key = api_key or config.get_api_key(cfg)

    if not current_api_key:
        print_error("OpenAI API Key not found.")
        print_info("Please run 'git-massage --setup' or set OPENAI_API_KEY env var.")

        if Prompt.ask("Do you want to run setup now?", choices=["y", "n"]) == "y":
            setup()
            cfg = config.load_config()
            current_api_key = config.get_api_key(cfg)
            if not current_api_key:
                raise typer.Exit(code=1)
        else:
            raise typer.Exit(code=1)

    try:
        # Exclude lockfiles
        excludes = [
            "package-lock.json",
            "uv.lock",
            "poetry.lock",
            "yarn.lock",
            "go.sum",
        ]
        diff = git.get_staged_diff(exclude_files=excludes)
    except git.GitError as e:
        print_error(str(e))
        raise typer.Exit(code=1)

    if not diff:
        print_error("No staged changes found. Did you run 'git add'?")
        raise typer.Exit(code=1)

    # Truncate if too long (simple char limit for now, spec says 4000 chars)
    max_chars = 4000
    if len(diff) > max_chars:
        diff = diff[:max_chars] + "\n[Diff truncated]"
        print_info("Diff is large, truncated for AI context.")

    while True:
        with console.status(
            f"Generating commit message using {current_model}...", spinner="dots"
        ):
            try:
                message = ai.generate_message(diff, current_model, current_api_key)
            except Exception:
                raise typer.Exit(code=1)

        console.print("\n[bold]Generated Commit Message:[/bold]")
        console.print(f"[dim]{'-' * 40}[/dim]")
        console.print(message)
        console.print(f"[dim]{'-' * 40}[/dim]\n")

        choice = Prompt.ask(
            "Action",
            choices=["c", "e", "r", "q"],
            default="c",
            show_choices=False,
            show_default=False,
        ).lower()

        console.print("[dim]Options: [c]ommit, [e]dit, [r]egenerate, [q]uit[/dim]")

        if choice == "c":
            try:
                git.commit(message)
                print_success("Committed successfully!")
                break
            except git.GitError as e:
                print_error(str(e))
                break

        elif choice == "e":
            edited_message = typer.edit(message)
            if edited_message:
                message = edited_message.strip()
                # Loop back to show the edited message and confirm again?
                # Usually user wants to commit immediately after edit or review again.
                # Let's show it again.
                continue
            else:
                print_info("Edit cancelled (empty message).")

        elif choice == "r":
            continue

        elif choice == "q":
            print_info("Aborted.")
            raise typer.Exit()


if __name__ == "__main__":
    app()
