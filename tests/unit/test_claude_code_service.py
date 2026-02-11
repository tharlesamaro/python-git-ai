"""Tests for ClaudeCodeAiService."""

import json

import pytest

from git_ai.config import GitAiConfig
from git_ai.services.claude_code_service import ClaudeCodeAiService


class TestClaudeCodeAiService:
    def test_can_be_instantiated(self) -> None:
        config = GitAiConfig(provider="claude-code")
        service = ClaudeCodeAiService(config)
        assert service is not None

    def test_parse_json_valid_response(self) -> None:
        config = GitAiConfig(provider="claude-code")
        service = ClaudeCodeAiService(config)
        text = json.dumps(
            {
                "type": "feat",
                "scope": "auth",
                "description": "add login",
                "body": "",
                "is_breaking_change": False,
            }
        )
        result = service._parse_json(text, ["type", "scope", "description"])
        assert result["type"] == "feat"
        assert result["scope"] == "auth"

    def test_parse_json_with_markdown_fences(self) -> None:
        config = GitAiConfig(provider="claude-code")
        service = ClaudeCodeAiService(config)
        text = '```json\n{"type": "fix", "scope": "", "description": "bug fix", "body": "", "is_breaking_change": false}\n```'
        result = service._parse_json(text, ["type"])
        assert result["type"] == "fix"

    def test_parse_json_raises_for_invalid_json(self) -> None:
        config = GitAiConfig(provider="claude-code")
        service = ClaudeCodeAiService(config)
        with pytest.raises(RuntimeError, match="Failed to parse"):
            service._parse_json("not json", ["type"])

    def test_parse_json_raises_for_missing_keys(self) -> None:
        config = GitAiConfig(provider="claude-code")
        service = ClaudeCodeAiService(config)
        text = json.dumps({"type": "feat"})
        with pytest.raises(RuntimeError, match="missing required key"):
            service._parse_json(text, ["type", "nonexistent"])

    def test_parse_changelog_response(self) -> None:
        config = GitAiConfig(provider="claude-code")
        service = ClaudeCodeAiService(config)
        text = json.dumps(
            {"sections": [{"type": "feat", "entries": ["Added login", "Added signup"]}]}
        )
        result = service._parse_json(text, ["sections"])
        assert len(result["sections"]) == 1
        assert result["sections"][0]["type"] == "feat"
