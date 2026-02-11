"""AI service implementation using Claude Code CLI."""

import json
import re
import shutil
import subprocess
from typing import Any

from git_ai.agents.prompts import build_changelog_prompt, build_commit_prompt
from git_ai.config import GitAiConfig
from git_ai.services.ai_service import AiService


class ClaudeCodeAiService(AiService):
    """
    Invokes the `claude` CLI installed on the user's machine.

    Allows usage through an existing Claude subscription without requiring
    a separate API key.
    """

    def __init__(self, config: GitAiConfig) -> None:
        self.config = config

    def generate_commit_message(self, diff: str) -> dict[str, Any]:
        prompt = build_commit_prompt(
            diff=diff,
            language=self.config.language,
            allowed_scopes=self.config.scopes,
            allowed_types=self.config.types,
            body_preference=self.config.commit.body,
        )
        result = self._run_claude(prompt)
        return self._parse_json(
            result, ["type", "scope", "description", "body", "is_breaking_change"]
        )

    def generate_changelog(self, prompt: str) -> dict[str, Any]:
        full_prompt = build_changelog_prompt(prompt, self.config.language)
        result = self._run_claude(full_prompt)
        return self._parse_json(result, ["sections"])

    def _run_claude(self, prompt: str) -> str:
        self._ensure_claude_cli_exists()

        command = ["claude", "-p", prompt, "--output-format", "json", "--max-turns", "1"]

        if self.config.model:
            command.extend(["--model", self.config.model])

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(
                f"Claude Code CLI failed (exit code {result.returncode}): "
                f"{(result.stderr or result.stdout).strip()}"
            )

        try:
            cli_response = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse Claude Code CLI output: {e}") from e

        if "result" not in cli_response:
            raise RuntimeError(
                'Unexpected Claude Code CLI response format: missing "result" field.'
            )

        return cli_response["result"]

    def _parse_json(self, text: str, required_keys: list[str]) -> dict[str, Any]:
        text = re.sub(r"^```(?:json)?\s*\n?", "", text, flags=re.MULTILINE)
        text = re.sub(r"\n?```\s*$", "", text, flags=re.MULTILINE)
        text = text.strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"Failed to parse AI response as JSON: {e}\nResponse: {text[:500]}"
            ) from e

        for key in required_keys:
            if key not in data:
                raise RuntimeError(f'AI response missing required key: "{key}".')
        return data

    def _ensure_claude_cli_exists(self) -> None:
        if shutil.which("claude") is None:
            raise RuntimeError(
                "Claude Code CLI not found. Please install it first: "
                "https://docs.anthropic.com/en/docs/claude-code"
            )
