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


def _filter_diff_noise(diff: str) -> str:
    """
    Filter out noise from git diff:
    1. Binary files - keep only the 'Binary files ... differ' line
    2. Deleted files - keep only filename and marker, strip diff content
    """
    if not diff:
        return diff

    lines = diff.split("\n")
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Binary files already show as "Binary files a/file and b/file differ"
        # Just keep this line and continue
        if line.startswith("Binary files"):
            result.append(line)
            i += 1
            continue

        # Detect deleted files: "diff --git a/file b/file" followed by "deleted file mode"
        if line.startswith("diff --git"):
            # Look ahead to see if this is a deletion
            j = i + 1
            is_deletion = False
            while j < len(lines) and j < i + 10:  # Check next ~10 lines
                if lines[j].startswith("deleted file mode"):
                    is_deletion = True
                    break
                if lines[j].startswith("diff --git"):  # Next file
                    break
                j += 1

            if is_deletion:
                # Include only the diff header and deleted marker
                result.append(line)  # diff --git line
                result.append("deleted file mode (content omitted)")
                # Skip all lines until next diff or end
                i += 1
                while i < len(lines) and not lines[i].startswith("diff --git"):
                    i += 1
                continue

        result.append(line)
        i += 1

    return "\n".join(result)


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

    diff_output = _run_git_command(cmd)

    # Apply noise filtering
    return _filter_diff_noise(diff_output)


def commit(message: str) -> None:
    try:
        _run_git_command(["commit", "-m", message])
    except GitError as e:
        raise GitError(f"Failed to commit: {e}")
