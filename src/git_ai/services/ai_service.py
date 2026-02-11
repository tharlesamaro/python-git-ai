"""Contract for AI service implementations."""

from abc import ABC, abstractmethod
from typing import Any


class AiService(ABC):
    """Defines the operations that any AI provider must support."""

    @abstractmethod
    def generate_commit_message(self, diff: str) -> dict[str, Any]:
        """
        Generate a commit message from a git diff.

        Returns dict with keys: type, scope, description, body, is_breaking_change
        """
        ...

    @abstractmethod
    def generate_changelog(self, prompt: str) -> dict[str, Any]:
        """
        Generate changelog sections from grouped commits.

        Returns dict with key: sections (list of {type, entries})
        """
        ...
