"""Tests for GitService with real git operations."""

import subprocess
from pathlib import Path

import pytest

from git_ai.services.git_service import GitService


class TestGitService:
    def test_detects_valid_git_repository(self, git_service: GitService) -> None:
        assert git_service.is_git_repository() is True

    def test_detects_non_git_directory(self, tmp_path: Path) -> None:
        service = GitService(working_directory=str(tmp_path))
        assert service.is_git_repository() is False

    def test_returns_empty_diff_when_nothing_staged(self, git_service: GitService) -> None:
        assert git_service.get_staged_diff() == ""

    def test_returns_diff_for_staged_changes(
        self, git_service: GitService, tmp_git_repo: Path
    ) -> None:
        (tmp_git_repo / "new_file.txt").write_text("hello world\n")
        subprocess.run(["git", "add", "new_file.txt"], cwd=tmp_git_repo, capture_output=True)
        diff = git_service.get_staged_diff()
        assert "hello world" in diff

    def test_returns_staged_stat(self, git_service: GitService, tmp_git_repo: Path) -> None:
        (tmp_git_repo / "new_file.txt").write_text("hello world\n")
        subprocess.run(["git", "add", "new_file.txt"], cwd=tmp_git_repo, capture_output=True)
        stat = git_service.get_staged_stat()
        assert "new_file.txt" in stat

    def test_has_staged_changes_false_when_clean(self, git_service: GitService) -> None:
        assert git_service.has_staged_changes() is False

    def test_has_staged_changes_true_when_staged(
        self, git_service: GitService, tmp_git_repo: Path
    ) -> None:
        (tmp_git_repo / "file.txt").write_text("content\n")
        subprocess.run(["git", "add", "file.txt"], cwd=tmp_git_repo, capture_output=True)
        assert git_service.has_staged_changes() is True

    def test_commit_with_message(self, git_service: GitService, tmp_git_repo: Path) -> None:
        (tmp_git_repo / "file.txt").write_text("content\n")
        subprocess.run(["git", "add", "file.txt"], cwd=tmp_git_repo, capture_output=True)
        git_service.commit("feat: add new file")
        result = subprocess.run(
            ["git", "log", "--oneline", "-1"],
            cwd=tmp_git_repo,
            capture_output=True,
            text=True,
        )
        assert "feat: add new file" in result.stdout

    def test_commit_raises_on_failure(self, git_service: GitService) -> None:
        with pytest.raises(RuntimeError, match="Git commit failed"):
            git_service.commit("should fail - nothing staged")

    def test_returns_none_when_no_tags(self, git_service: GitService) -> None:
        assert git_service.get_latest_tag() is None

    def test_returns_latest_tag(self, git_service: GitService, tmp_git_repo: Path) -> None:
        subprocess.run(["git", "tag", "v1.0.0"], cwd=tmp_git_repo, capture_output=True)
        assert git_service.get_latest_tag() == "v1.0.0"

    def test_returns_all_tags(self, git_service: GitService, tmp_git_repo: Path) -> None:
        subprocess.run(["git", "tag", "v1.0.0"], cwd=tmp_git_repo, capture_output=True)
        # Create a new commit so we can add another tag
        (tmp_git_repo / "file.txt").write_text("v2\n")
        subprocess.run(["git", "add", "."], cwd=tmp_git_repo, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "feat: v2"],
            cwd=tmp_git_repo,
            capture_output=True,
        )
        subprocess.run(["git", "tag", "v2.0.0"], cwd=tmp_git_repo, capture_output=True)
        tags = git_service.get_all_tags()
        assert "v1.0.0" in tags
        assert "v2.0.0" in tags

    def test_returns_first_commit_hash(self, git_service: GitService) -> None:
        first_hash = git_service.get_first_commit_hash()
        assert first_hash is not None
        assert len(first_hash) == 40

    def test_returns_commits_between_refs(
        self, git_service: GitService, tmp_git_repo: Path
    ) -> None:
        subprocess.run(["git", "tag", "v1.0.0"], cwd=tmp_git_repo, capture_output=True)
        (tmp_git_repo / "file.txt").write_text("new\n")
        subprocess.run(["git", "add", "."], cwd=tmp_git_repo, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "feat: new feature"],
            cwd=tmp_git_repo,
            capture_output=True,
        )
        commits = git_service.get_commits_between("v1.0.0", "HEAD")
        assert len(commits) == 1
        assert commits[0]["message"] == "feat: new feature"

    def test_returns_empty_when_no_commits_between(self, git_service: GitService) -> None:
        subprocess.run(
            ["git", "tag", "v1.0.0"],
            cwd=git_service.working_directory,
            capture_output=True,
        )
        commits = git_service.get_commits_between("v1.0.0", "HEAD")
        assert commits == []

    def test_get_hooks_path(self, git_service: GitService, tmp_git_repo: Path) -> None:
        hooks_path = git_service.get_hooks_path()
        assert Path(hooks_path).exists()
        assert "hooks" in hooks_path

    def test_add_all(self, git_service: GitService, tmp_git_repo: Path) -> None:
        (tmp_git_repo / "untracked.txt").write_text("new file\n")
        git_service.add_all()
        assert git_service.has_staged_changes() is True
