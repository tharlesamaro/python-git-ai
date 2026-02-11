"""Tests for AI service factory and contracts."""

import pytest

from git_ai.config import GitAiConfig
from git_ai.services.ai_service import AiService
from git_ai.services.factory import resolve_ai_service


class TestAiServiceContract:
    def test_defines_generate_commit_message(self) -> None:
        assert hasattr(AiService, "generate_commit_message")

    def test_defines_generate_changelog(self) -> None:
        assert hasattr(AiService, "generate_changelog")


class TestResolveAiService:
    def test_resolves_anthropic_by_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        from git_ai.services.anthropic_service import AnthropicAiService

        config = GitAiConfig(provider="anthropic")
        service = resolve_ai_service(config)
        assert isinstance(service, AnthropicAiService)

    def test_resolves_openai(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        from git_ai.services.openai_service import OpenAiService

        config = GitAiConfig(provider="openai")
        service = resolve_ai_service(config)
        assert isinstance(service, OpenAiService)

    def test_resolves_claude_code(self) -> None:
        from git_ai.services.claude_code_service import ClaudeCodeAiService

        config = GitAiConfig(provider="claude-code")
        service = resolve_ai_service(config)
        assert isinstance(service, ClaudeCodeAiService)

    def test_anthropic_raises_without_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        config = GitAiConfig(provider="anthropic")
        with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
            resolve_ai_service(config)

    def test_openai_raises_without_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        config = GitAiConfig(provider="openai")
        with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
            resolve_ai_service(config)
