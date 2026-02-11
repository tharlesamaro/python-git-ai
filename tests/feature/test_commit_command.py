"""Feature tests for the commit command."""

from unittest.mock import patch

from typer.testing import CliRunner

from git_ai.cli import app
from git_ai.config import GitAiConfig

runner = CliRunner()


class TestCommitCommand:
    def test_fails_when_not_git_repository(self, tmp_path: str) -> None:
        with patch("git_ai.cli.GitService") as mock_git:
            mock_git.return_value.is_git_repository.return_value = False
            result = runner.invoke(app, ["commit"])
            assert result.exit_code != 0
            assert "not a Git repository" in result.output

    def test_warns_when_no_staged_changes(self) -> None:
        with patch("git_ai.cli.GitService") as mock_git:
            mock_git.return_value.is_git_repository.return_value = True
            mock_git.return_value.has_staged_changes.return_value = False
            result = runner.invoke(app, ["commit"])
            assert result.exit_code != 0
            assert "No staged changes" in result.output

    def test_stages_all_when_all_flag(self) -> None:
        with (
            patch("git_ai.cli.GitService") as mock_git,
            patch("git_ai.cli.load_config", return_value=GitAiConfig()),
        ):
            instance = mock_git.return_value
            instance.is_git_repository.return_value = True
            instance.has_staged_changes.return_value = False
            runner.invoke(app, ["commit", "--all"])
            instance.add_all.assert_called_once()

    def test_fails_with_invalid_template(self) -> None:
        with (
            patch("git_ai.cli.GitService") as mock_git,
            patch("git_ai.cli.load_config", return_value=GitAiConfig()),
        ):
            mock_git.return_value.is_git_repository.return_value = True
            result = runner.invoke(app, ["commit", "--template", "nonexistent"])
            assert result.exit_code != 0
            assert "Unknown commit template" in result.output

    def test_accepts_minimal_template(self) -> None:
        with (
            patch("git_ai.cli.GitService") as mock_git,
            patch("git_ai.cli.load_config", return_value=GitAiConfig()),
        ):
            instance = mock_git.return_value
            instance.is_git_repository.return_value = True
            instance.has_staged_changes.return_value = False
            result = runner.invoke(app, ["commit", "--template", "minimal"])
            assert "Unknown commit template" not in result.output

    def test_accepts_no_body_flag(self) -> None:
        with (
            patch("git_ai.cli.GitService") as mock_git,
            patch("git_ai.cli.load_config", return_value=GitAiConfig()),
        ):
            instance = mock_git.return_value
            instance.is_git_repository.return_value = True
            instance.has_staged_changes.return_value = False
            result = runner.invoke(app, ["commit", "--no-body"])
            assert "Unknown" not in result.output


class TestCommitCommandHelp:
    def test_shows_help(self) -> None:
        result = runner.invoke(app, ["commit", "--help"])
        assert result.exit_code == 0
        assert "Conventional Commits" in result.output
        assert "--all" in result.output
        assert "--template" in result.output
