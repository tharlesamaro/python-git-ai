"""Feature tests for the setup command."""

from typer.testing import CliRunner

from git_ai.cli import app

runner = CliRunner()


class TestSetupCommand:
    def test_registers_setup_command(self) -> None:
        result = runner.invoke(app, ["setup", "--help"])
        assert result.exit_code == 0
        assert "Interactive setup" in result.output

    def test_registers_commit_command(self) -> None:
        result = runner.invoke(app, ["commit", "--help"])
        assert result.exit_code == 0

    def test_registers_changelog_command(self) -> None:
        result = runner.invoke(app, ["changelog", "--help"])
        assert result.exit_code == 0

    def test_version_flag(self) -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "git-ai version" in result.output
