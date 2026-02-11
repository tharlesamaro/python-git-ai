"""CLI commands for Git AI using Typer."""

import os
import re
import shutil
import stat
from datetime import date
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from git_ai.__version__ import __version__
from git_ai.config import GitAiConfig, load_config
from git_ai.enums import CommitType
from git_ai.services.ai_service import AiService
from git_ai.services.factory import resolve_ai_service
from git_ai.services.git_service import GitService
from git_ai.support.commit_template import CommitTemplate

app = typer.Typer(
    name="git-ai",
    help="🤖 AI-powered Git workflow automation",
    add_completion=False,
)

console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"git-ai version: [bold]{__version__}[/bold]")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = None,
) -> None:
    """
    Git AI - AI-powered Git workflow automation for Python.

    Generate commit messages, changelogs, and validate commits using AI.
    """


# ---------------------------------------------------------------------------
# commit
# ---------------------------------------------------------------------------


@app.command()
def commit(
    all: Annotated[
        bool, typer.Option("--all", "-a", help="Stage all changes before committing")
    ] = False,
    template: Annotated[
        str | None, typer.Option(help="Use a named commit template (e.g. minimal, detailed)")
    ] = None,
    no_body: Annotated[
        bool, typer.Option("--no-body", help="Strip body from the commit message")
    ] = False,
    footer: Annotated[list[str] | None, typer.Option(help="Add custom footer line(s)")] = None,
) -> None:
    """
    Generate AI-powered commit message following Conventional Commits.

    Examples:

        $ git add .

        $ git-ai commit

        $ git-ai commit --all

        $ git-ai commit --template=minimal
    """
    config = load_config()
    git = GitService()

    if not git.is_git_repository():
        console.print("[red]This directory is not a Git repository.[/red]")
        raise typer.Exit(1)

    # Resolve template
    try:
        tmpl = CommitTemplate.resolve(template, config)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    # Apply CLI overrides
    body_override = "never" if no_body else None
    footer_override = footer if footer else None
    if body_override or footer_override:
        tmpl = tmpl.with_overrides(body=body_override, extra_footer_lines=footer_override)

    # Override body preference in config so AI services pick it up
    if tmpl.body == "always":
        config.commit.body = "always"

    # Stage all if requested
    if all:
        git.add_all()

    if not git.has_staged_changes():
        console.print(
            "[yellow]No staged changes found. Use `git add` to stage your changes first, "
            "or run with --all flag.[/yellow]"
        )
        raise typer.Exit(1)

    diff = _prepare_diff(git, config)
    stat_output = git.get_staged_stat()
    console.print(f"\n[dim]Staged changes:[/dim]\n{stat_output}\n")

    # Resolve AI service
    try:
        ai = resolve_ai_service(config)
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    commit_message = _generate_commit_message(ai, diff, tmpl, config)
    if commit_message is None:
        raise typer.Exit(1)

    _handle_user_choice(git, ai, commit_message, diff, tmpl, config)


def _prepare_diff(git: GitService, config: GitAiConfig) -> str:
    diff = git.get_staged_diff()
    max_size = config.max_diff_size
    if len(diff) <= max_size:
        return diff
    console.print("[yellow]Diff is too large. Truncating to fit the AI context window.[/yellow]")
    return diff[:max_size] + "\n\n[... diff truncated ...]"


def _generate_commit_message(
    ai: AiService, diff: str, tmpl: CommitTemplate, config: GitAiConfig
) -> str | None:
    try:
        with console.status("Generating commit message..."):
            response = ai.generate_commit_message(diff)
        return _format_commit_message(response, tmpl, config)
    except Exception as e:
        console.print(f"[red]Failed to generate commit message: {e}[/red]")
        return None


def _format_commit_message(response: dict, tmpl: CommitTemplate, config: GitAiConfig) -> str:
    commit_type = response.get("type", "")
    scope = response.get("scope", "")
    description = response.get("description", "")
    body = response.get("body", "")
    is_breaking = response.get("is_breaking_change", False)

    # Validate type against allowed types
    if config.types and commit_type not in config.types:
        commit_type = config.types[0]

    # Validate scope against allowed scopes
    if config.scopes and scope and scope not in config.scopes:
        scope = ""

    # Strip body if template says never
    if tmpl.body == "never":
        body = ""

    # Build first line
    first_line = commit_type
    if scope:
        first_line += f"({scope})"
    if is_breaking:
        first_line += "!"
    first_line += f": {description}"

    message = first_line
    if body:
        message += f"\n\n{body}"

    # Build footers
    footers: list[str] = []
    if is_breaking and tmpl.breaking_change_footer:
        footers.append(f"BREAKING CHANGE: {description}")
    if tmpl.co_authored_by:
        provider = config.provider
        model = config.model or ("GPT" if provider == "openai" else "Claude")
        footers.append(f"Co-Authored-By: {model} <noreply@{provider}.com>")
    footers.extend(tmpl.footer_lines)

    if footers:
        message += "\n\n" + "\n".join(footers)

    return message


def _handle_user_choice(
    git: GitService,
    ai: AiService,
    commit_message: str,
    diff: str,
    tmpl: CommitTemplate,
    config: GitAiConfig,
) -> None:
    while True:
        console.print("\n[bold]Generated commit message:[/bold]")
        console.print(Panel(commit_message, border_style="green"))

        choice = Prompt.ask(
            "What would you like to do?",
            choices=["accept", "edit", "regenerate", "cancel"],
            default="accept",
        )

        match choice:
            case "accept":
                try:
                    git.commit(commit_message)
                    console.print("[green]✅ Commit created successfully![/green]")
                    return
                except RuntimeError as e:
                    console.print(f"[red]Failed to create commit: {e}[/red]")
                    raise typer.Exit(1)
            case "edit":
                commit_message = _edit_message(commit_message)
            case "regenerate":
                new_msg = _generate_commit_message(ai, diff, tmpl, config)
                if new_msg is None:
                    raise typer.Exit(1)
                commit_message = new_msg
            case "cancel":
                console.print("[yellow]Commit cancelled.[/yellow]")
                return


def _edit_message(current: str) -> str:
    lines = current.split("\n")
    first_line = lines[0]
    body = "\n".join(lines[2:]) if len(lines) > 2 else ""

    edited_first = Prompt.ask("Edit the commit title", default=first_line)
    edited_body = Prompt.ask("Edit the commit body (leave empty to remove)", default=body)

    message = edited_first
    if edited_body.strip():
        message += f"\n\n{edited_body}"
    return message


# ---------------------------------------------------------------------------
# changelog
# ---------------------------------------------------------------------------


@app.command()
def changelog(
    from_ref: Annotated[
        str | None, typer.Option("--from", help="Starting reference (tag/commit)")
    ] = None,
    to_ref: Annotated[str, typer.Option("--to", help="Ending reference")] = "HEAD",
    tag: Annotated[str | None, typer.Option(help="Version tag for the changelog")] = None,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Preview without writing to file")
    ] = False,
) -> None:
    """
    Generate changelog from commits using AI.

    Examples:

        $ git-ai changelog --tag v2.0.0

        $ git-ai changelog --from v1.0.0 --to v2.0.0

        $ git-ai changelog --tag v2.0.0 --dry-run
    """
    config = load_config()
    git = GitService()

    if not git.is_git_repository():
        console.print("[red]This directory is not a Git repository.[/red]")
        raise typer.Exit(1)

    resolved_from = _resolve_from_reference(git, from_ref)
    if resolved_from is None:
        console.print(
            "[red]Could not determine a starting point. Use --from to specify a tag or commit hash.[/red]"
        )
        raise typer.Exit(1)

    commits = git.get_commits_between(resolved_from, to_ref)
    if not commits:
        console.print(f"[yellow]No commits found between {resolved_from} and {to_ref}.[/yellow]")
        return

    console.print(
        f"[blue]Found {len(commits)} commits between {resolved_from} and {to_ref}.[/blue]"
    )

    grouped = _group_commits_by_type(commits)

    try:
        ai = resolve_ai_service(config)
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(1)

    changelog_sections = _generate_changelog(ai, grouped)
    if changelog_sections is None:
        raise typer.Exit(1)

    version_tag = tag or Prompt.ask("What version tag should this changelog use?", default="v1.0.0")
    formatted = _format_changelog(version_tag, changelog_sections, config)

    console.print("\n[dim]Preview:[/dim]")
    console.print(Panel(formatted, border_style="blue"))

    if dry_run:
        console.print("[blue]Dry run complete. No files were written.[/blue]")
        return

    if not Confirm.ask("Write this changelog to file?", default=True):
        console.print("[yellow]Changelog generation cancelled.[/yellow]")
        return

    _write_changelog(formatted, config)


def _resolve_from_reference(git: GitService, from_ref: str | None) -> str | None:
    if from_ref:
        return from_ref

    if latest_tag := git.get_latest_tag():
        console.print(f"[blue]Using latest tag as starting point: {latest_tag}[/blue]")
        return latest_tag

    if first_commit := git.get_first_commit_hash():
        console.print("[blue]No tags found. Using first commit as starting point.[/blue]")
        return first_commit

    return None


def _group_commits_by_type(commits: list[dict[str, str]]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = {}
    pattern = re.compile(
        r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]+)\))?!?:\s*(?P<description>.+)$", re.I
    )

    for commit in commits:
        msg = commit["message"]
        if m := pattern.match(msg):
            ctype = m.group("type").lower()
            grouped.setdefault(ctype, []).append(msg)
        else:
            grouped.setdefault("other", []).append(msg)

    return grouped


def _generate_changelog(ai: AiService, grouped: dict[str, list[str]]) -> list[dict] | None:
    prompt = "Generate a changelog from these grouped commits:\n\n"
    for ctype, messages in grouped.items():
        prompt += f"## {ctype}\n"
        for msg in messages:
            prompt += f"- {msg}\n"
        prompt += "\n"

    try:
        with console.status("Generating changelog..."):
            response = ai.generate_changelog(prompt)
        return response.get("sections", [])
    except Exception as e:
        console.print(f"[red]Failed to generate changelog: {e}[/red]")
        return None


def _format_changelog(version_tag: str, sections: list[dict], config: GitAiConfig) -> str:
    with_emojis = config.changelog.with_emojis
    today = date.today().isoformat()

    lines = [f"## [{version_tag}] - {today}", ""]

    for section in sections:
        ctype = section.get("type", "other")
        entries = section.get("entries", [])
        if not entries:
            continue

        try:
            commit_type = CommitType(ctype)
            label = commit_type.label
            emoji = f"{commit_type.emoji} " if with_emojis else ""
        except ValueError:
            label = ctype.capitalize()
            emoji = ""

        lines.append(f"### {emoji}{label}")
        lines.append("")
        for entry in entries:
            lines.append(f"- {entry}")
        lines.append("")

    return "\n".join(lines)


def _write_changelog(new_content: str, config: GitAiConfig) -> None:
    changelog_path = Path(config.changelog.path)
    header = (
        "# Changelog\n\nAll notable changes to this project will be documented in this file.\n\n"
    )

    existing = ""
    if changelog_path.is_file():
        existing = changelog_path.read_text()
        existing = re.sub(r"^# Changelog\n+.*?(?=## \[)", "", existing, flags=re.DOTALL)

    full_content = header + new_content + existing
    changelog_path.write_text(full_content)
    console.print(f"[green]Changelog written to {changelog_path}[/green]")


# ---------------------------------------------------------------------------
# setup
# ---------------------------------------------------------------------------


@app.command()
def setup() -> None:
    """
    Interactive setup for Git AI configuration.

    Walks you through configuring:
    - AI provider (Anthropic/OpenAI/Claude Code)
    - Language for commit messages
    - Project-specific scopes and types
    - Git hook installation

    Examples:

        $ git-ai setup
    """
    console.print(
        Panel.fit(
            "🚀 [bold]Git AI - Setup[/bold]",
            border_style="magenta",
        )
    )
    console.print("[dim]This wizard will configure your AI-powered Git workflow.[/dim]\n")

    provider = _ask_provider()
    language = _ask_language()
    scopes = _ask_scopes()
    types = _ask_types()
    body_preference = _ask_body_preference()

    git = GitService()
    install_hook = _ask_hook(git)

    _write_config_file(provider, language, scopes, types, body_preference, install_hook)

    if install_hook:
        _install_git_hook(git)

    _write_env_hints(provider, language)

    console.print("\n[green]✅ Setup complete! You can now use:[/green]")
    console.print("  [dim]git-ai commit[/dim]     - Generate AI commit messages")
    console.print("  [dim]git-ai changelog[/dim]  - Generate changelogs\n")


def _ask_provider() -> str:
    return Prompt.ask(
        "Which AI provider do you want to use?",
        choices=["anthropic", "openai", "claude-code"],
        default="anthropic",
    )


def _ask_language() -> str:
    options = {
        "en": "English",
        "pt-BR": "Português (Brasil)",
        "es": "Español",
        "fr": "Français",
        "de": "Deutsch",
        "it": "Italiano",
        "ja": "日本語",
        "ko": "한국어",
        "zh": "中文",
    }
    console.print("\n[bold]Available languages:[/bold]")
    for code, name in options.items():
        console.print(f"  [cyan]{code}[/cyan] - {name}")

    return Prompt.ask(
        "\nLanguage for commit messages",
        choices=list(options.keys()),
        default="en",
    )


def _ask_scopes() -> list[str]:
    if not Confirm.ask(
        "Do you want to define allowed commit scopes for this project?", default=False
    ):
        return []

    scopes_input = Prompt.ask("Enter the allowed scopes (comma-separated)", default="")
    return [s.strip() for s in scopes_input.split(",") if s.strip()]


def _ask_types() -> list[str]:
    if not Confirm.ask("Do you want to restrict which commit types are allowed?", default=False):
        return []

    console.print("\n[bold]Available commit types:[/bold]")
    for ct in CommitType:
        console.print(f"  [cyan]{ct.value}[/cyan] - {ct.description}")

    types_input = Prompt.ask(
        "\nEnter the allowed types (comma-separated)",
        default="feat,fix,docs,refactor,test,chore",
    )
    valid_values = CommitType.values()
    return [t.strip() for t in types_input.split(",") if t.strip() in valid_values]


def _ask_body_preference() -> str:
    return Prompt.ask(
        "How should commit message body be handled? (auto/always/never)",
        choices=["auto", "always", "never"],
        default="auto",
    )


def _ask_hook(git: GitService) -> bool:
    if not git.is_git_repository():
        console.print("[yellow]Not a Git repository. Skipping hook installation.[/yellow]")
        return False
    return Confirm.ask("Install a Git hook to validate commit messages?", default=True)


def _write_config_file(
    provider: str,
    language: str,
    scopes: list[str],
    types: list[str],
    body_preference: str,
    hook_enabled: bool,
) -> None:
    scopes_str = _list_to_toml(scopes)
    types_str = _list_to_toml(types)

    config_content = f"""[git-ai]
provider = "{provider}"
language = "{language}"
scopes = {scopes_str}
types = {types_str}
max_diff_size = 15000

[git-ai.commit]
body = "{body_preference}"

[git-ai.commit.footer]
breaking_change = true
co_authored_by = false
lines = []

[git-ai.templates]

[git-ai.changelog]
path = "CHANGELOG.md"
with_emojis = true

[git-ai.hook]
enabled = {"true" if hook_enabled else "false"}
strict = true
"""

    config_path = Path(".git-ai.toml")
    config_path.write_text(config_content)
    console.print(f"[green]Configuration written to {config_path}[/green]")


def _install_git_hook(git: GitService) -> None:
    hooks_path = git.get_hooks_path()
    hook_dest = os.path.join(hooks_path, "commit-msg")
    stub_path = Path(__file__).parent.parent.parent / "hooks" / "commit-msg"

    if not stub_path.is_file():
        stub_path = Path(__file__).parent / "hooks" / "commit-msg"

    if not stub_path.is_file():
        console.print("[red]Hook stub file not found.[/red]")
        return

    shutil.copy2(str(stub_path), hook_dest)
    os.chmod(hook_dest, os.stat(hook_dest).st_mode | stat.S_IEXEC)
    console.print(f"[green]Git hook installed at {hook_dest}[/green]")


def _write_env_hints(provider: str, language: str) -> None:
    console.print("\n[dim]Add these environment variables:[/dim]\n")

    match provider:
        case "claude-code":
            console.print(f"  [yellow]GIT_AI_PROVIDER[/yellow]={provider}")
            console.print(f"  [yellow]GIT_AI_LANGUAGE[/yellow]={language}")
            console.print(
                "\n[dim]No API key required. Make sure Claude Code CLI is installed and configured.[/dim]"
            )
        case _:
            env_key = "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
            console.print(f"  [yellow]{env_key}[/yellow]=your-api-key")
            console.print(f"  [yellow]GIT_AI_PROVIDER[/yellow]={provider}")
            console.print(f"  [yellow]GIT_AI_LANGUAGE[/yellow]={language}")


def _list_to_toml(items: list[str]) -> str:
    if not items:
        return "[]"
    inner = ", ".join(f'"{item}"' for item in items)
    return f"[{inner}]"


if __name__ == "__main__":
    app()
