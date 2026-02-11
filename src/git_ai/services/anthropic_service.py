"""AI service implementation using the Anthropic API."""

import json
import os
import re
from typing import Any

import anthropic

from git_ai.agents.prompts import build_changelog_prompt, build_commit_prompt
from git_ai.config import GitAiConfig
from git_ai.services.ai_service import AiService


class AnthropicAiService(AiService):
    """Uses the Anthropic Claude API to generate commit messages and changelogs."""

    def __init__(self, config: GitAiConfig) -> None:
        self.config = config
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Please set it or run 'git-ai setup' to configure."
            )
        self.client = anthropic.Anthropic(api_key=api_key)

    def generate_commit_message(self, diff: str) -> dict[str, Any]:
        prompt = build_commit_prompt(
            diff=diff,
            language=self.config.language,
            allowed_scopes=self.config.scopes,
            allowed_types=self.config.types,
            body_preference=self.config.commit.body,
        )
        response = self._call(prompt)
        return self._parse_json(
            response, ["type", "scope", "description", "body", "is_breaking_change"]
        )

    def generate_changelog(self, prompt: str) -> dict[str, Any]:
        full_prompt = build_changelog_prompt(prompt, self.config.language)
        response = self._call(full_prompt)
        return self._parse_json(response, ["sections"])

    def _call(self, prompt: str) -> str:
        model = self.config.model or "claude-sonnet-4-20250514"
        message = self.client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text

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
