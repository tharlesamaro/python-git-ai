"""Service responsible for all Git interactions."""

import os
import subprocess
from pathlib import Path


class GitService:
    """Encapsulates Git commands in typed and testable methods."""

    def __init__(self, working_directory: str | None = None) -> None:
        self.working_directory = working_directory or os.getcwd()

    def is_git_repository(self) -> bool:
        result = self._run("git rev-parse --is-inside-work-tree")
        return result.returncode == 0 and result.stdout.strip() == "true"

    def get_staged_diff(self) -> str:
        result = self._run("git diff --staged")
        return result.stdout.strip() if result.returncode == 0 else ""

    def get_staged_stat(self) -> str:
        result = self._run("git diff --staged --stat")
        return result.stdout.strip() if result.returncode == 0 else ""

    def has_staged_changes(self) -> bool:
        return self.get_staged_diff() != ""

    def add_all(self) -> None:
        result = self._run("git add -A")
        if result.returncode != 0:
            raise RuntimeError(f"Git add failed: {result.stderr}")

    def commit(self, message: str) -> None:
        result = self._run(["git", "commit", "-m", message], shell=False)
        if result.returncode != 0:
            raise RuntimeError(f"Git commit failed: {result.stderr}")

    def get_commits_between(self, from_ref: str, to_ref: str = "HEAD") -> list[dict[str, str]]:
        result = self._run(
            ["git", "log", f"{from_ref}..{to_ref}", "--pretty=format:%H|%s"],
            shell=False,
        )
        if result.returncode != 0 or not result.stdout.strip():
            return []

        commits = []
        for line in result.stdout.strip().split("\n"):
            parts = line.split("|", 1)
            if len(parts) == 2 and parts[0] and parts[1]:
                commits.append({"hash": parts[0], "message": parts[1]})
        return commits

    def get_latest_tag(self) -> str | None:
        result = self._run("git describe --tags --abbrev=0")
        if result.returncode != 0 or not result.stdout.strip():
            return None
        return result.stdout.strip()

    def get_all_tags(self) -> list[str]:
        result = self._run(
            'git for-each-ref --sort=-committerdate --format="%(refname:short)" refs/tags'
        )
        if result.returncode != 0 or not result.stdout.strip():
            return []
        return [t.strip('"') for t in result.stdout.strip().split("\n") if t.strip()]

    def get_first_commit_hash(self) -> str | None:
        result = self._run("git rev-list --max-parents=0 HEAD")
        if result.returncode != 0 or not result.stdout.strip():
            return None
        return result.stdout.strip().split("\n")[0]

    def get_hooks_path(self) -> str:
        result = self._run("git config core.hooksPath")
        if result.returncode == 0 and result.stdout.strip():
            hooks_path = result.stdout.strip()
        else:
            hooks_path = os.path.join(self.working_directory, ".git", "hooks")

        Path(hooks_path).mkdir(parents=True, exist_ok=True)
        return hooks_path

    def _run(
        self, command: str | list[str], shell: bool = True
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=self.working_directory,
            shell=shell,
        )
