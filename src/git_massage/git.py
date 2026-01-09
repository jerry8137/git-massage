import subprocess
import shutil
from typing import List, Optional


class GitError(Exception):
    pass


def _run_git_command(args: List[str]) -> str:
    try:
        if not shutil.which("git"):
            raise GitError("Git is not installed or not in PATH.")

        result = subprocess.run(
            ["git"] + args, capture_output=True, text=True, check=False
        )

        if result.returncode != 0:
            raise GitError(f"Git command failed: {result.stderr.strip()}")

        return result.stdout.strip()
    except FileNotFoundError:
        raise GitError("Git executable not found.")
    except Exception as e:
        raise GitError(f"Unexpected error running git: {str(e)}")


def get_staged_diff(exclude_files: Optional[List[str]] = None) -> str:
    try:
        _run_git_command(["rev-parse", "--is-inside-work-tree"])
    except GitError:
        raise GitError("Not a git repository.")

    staged_files_output = _run_git_command(["diff", "--cached", "--name-only"])
    staged_files = staged_files_output.splitlines()

    if not staged_files:
        return ""

    cmd = ["diff", "--cached"]

    if exclude_files:
        for f in exclude_files:
            cmd.append(f":(exclude){f}")

    return _run_git_command(cmd)


def commit(message: str) -> None:
    try:
        _run_git_command(["commit", "-m", message])
    except GitError as e:
        raise GitError(f"Failed to commit: {e}")
