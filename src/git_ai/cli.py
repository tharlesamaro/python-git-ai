"""CLI commands for Git AI using Typer."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from typing import Optional

from git_ai.__version__ import __version__

app = typer.Typer(
    name="git-ai",
    help="🤖 AI-powered Git workflow automation",
    add_completion=False,
)

console = Console()


def version_callback(value: bool):
    """Print version and exit."""
    if value:
        console.print(f"git-ai version: [bold]{__version__}[/bold]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
):
    """
    Git AI - AI-powered Git workflow automation for Python.

    Generate commit messages, changelogs, and validate commits using AI.
    """
    pass


@app.command()
def commit(
    all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Stage all changes before committing",
    ),
):
    """
    Generate AI-powered commit message following Conventional Commits.

    Examples:

        $ git add .

        $ git-ai commit

        $ git-ai commit --all
    """
    console.print(
        Panel.fit(
            "🚀 [bold]Git AI Commit[/bold]",
            border_style="blue",
        )
    )

    # TODO: Implement commit logic
    console.print("⚠️  [yellow]Not implemented yet[/yellow]")


@app.command()
def changelog(
    from_ref: Optional[str] = typer.Option(
        None,
        "--from",
        help="Starting reference (tag/commit)",
    ),
    to_ref: str = typer.Option(
        "HEAD",
        "--to",
        help="Ending reference",
    ),
    tag: Optional[str] = typer.Option(
        None,
        "--tag",
        help="Version tag for the changelog",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview without writing to file",
    ),
):
    """
    Generate changelog from commits using AI.

    Examples:

        $ git-ai changelog --tag v2.0.0

        $ git-ai changelog --from v1.0.0 --to v2.0.0

        $ git-ai changelog --tag v2.0.0 --dry-run
    """
    console.print(
        Panel.fit(
            "📝 [bold]Git AI Changelog[/bold]",
            border_style="green",
        )
    )

    # TODO: Implement changelog logic
    console.print("⚠️  [yellow]Not implemented yet[/yellow]")


@app.command()
def setup():
    """
    Interactive setup for Git AI configuration.

    Walks you through configuring:
    - AI provider (Anthropic/OpenAI)
    - Language for commit messages
    - Project-specific scopes and types
    - Git hook installation

    Examples:

        $ git-ai setup
    """
    console.print(
        Panel.fit(
            "⚙️  [bold]Git AI Setup[/bold]",
            border_style="magenta",
        )
    )

    # TODO: Implement setup logic
    console.print("⚠️  [yellow]Not implemented yet[/yellow]")


if __name__ == "__main__":
    app()
