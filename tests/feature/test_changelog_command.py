"""Feature tests for the changelog command."""

from unittest.mock import patch

from typer.testing import CliRunner

from git_ai.cli import app

runner = CliRunner()


class TestChangelogCommand:
    def test_fails_when_not_git_repository(self) -> None:
        with patch("git_ai.cli.GitService") as mock_git:
            mock_git.return_value.is_git_repository.return_value = False
            result = runner.invoke(app, ["changelog"])
            assert result.exit_code != 0
            assert "not a Git repository" in result.output

    def test_fails_when_no_starting_point(self) -> None:
        with (
            patch("git_ai.cli.GitService") as mock_git,
            patch("git_ai.cli.load_config"),
        ):
            instance = mock_git.return_value
            instance.is_git_repository.return_value = True
            instance.get_latest_tag.return_value = None
            instance.get_first_commit_hash.return_value = None
            result = runner.invoke(app, ["changelog"])
            assert result.exit_code != 0
            assert "Could not determine a starting point" in result.output

    def test_warns_when_no_commits_found(self) -> None:
        with (
            patch("git_ai.cli.GitService") as mock_git,
            patch("git_ai.cli.load_config"),
        ):
            instance = mock_git.return_value
            instance.is_git_repository.return_value = True
            instance.get_latest_tag.return_value = None
            instance.get_first_commit_hash.return_value = "abc123"
            instance.get_commits_between.return_value = []
            result = runner.invoke(app, ["changelog", "--from", "abc123"])
            assert "No commits found" in result.output

    def test_uses_from_option(self) -> None:
        with (
            patch("git_ai.cli.GitService") as mock_git,
            patch("git_ai.cli.load_config"),
        ):
            instance = mock_git.return_value
            instance.is_git_repository.return_value = True
            instance.get_commits_between.return_value = []
            runner.invoke(app, ["changelog", "--from", "v1.0.0"])
            instance.get_commits_between.assert_called_once_with("v1.0.0", "HEAD")


class TestChangelogCommandHelp:
    def test_shows_help(self) -> None:
        result = runner.invoke(app, ["changelog", "--help"])
        assert result.exit_code == 0
        assert "--from" in result.output
        assert "--to" in result.output
        assert "--tag" in result.output
        assert "--dry-run" in result.output
