"""Factory for resolving the appropriate AI service."""

from git_ai.config import GitAiConfig
from git_ai.services.ai_service import AiService


def resolve_ai_service(config: GitAiConfig) -> AiService:
    """Resolve the AI service based on the provider configuration."""
    match config.provider:
        case "claude-code":
            from git_ai.services.claude_code_service import ClaudeCodeAiService

            return ClaudeCodeAiService(config)
        case "openai":
            from git_ai.services.openai_service import OpenAiService

            return OpenAiService(config)
        case _:
            from git_ai.services.anthropic_service import AnthropicAiService

            return AnthropicAiService(config)
