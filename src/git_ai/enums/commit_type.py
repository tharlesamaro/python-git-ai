"""Commit types according to the Conventional Commits specification."""

from enum import Enum


class CommitType(Enum):
    """
    Commit types according to the Conventional Commits specification.

    Each case represents a valid commit type, with label and description
    for use in message generation and validation.

    See: https://www.conventionalcommits.org/en/v1.0.0/
    """

    FEAT = "feat"
    FIX = "fix"
    DOCS = "docs"
    STYLE = "style"
    REFACTOR = "refactor"
    PERF = "perf"
    TEST = "test"
    BUILD = "build"
    CI = "ci"
    CHORE = "chore"
    REVERT = "revert"

    @property
    def description(self) -> str:
        descriptions = {
            CommitType.FEAT: "A new feature",
            CommitType.FIX: "A bug fix",
            CommitType.DOCS: "Documentation only changes",
            CommitType.STYLE: "Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)",
            CommitType.REFACTOR: "A code change that neither fixes a bug nor adds a feature",
            CommitType.PERF: "A code change that improves performance",
            CommitType.TEST: "Adding missing tests or correcting existing tests",
            CommitType.BUILD: "Changes that affect the build system or external dependencies",
            CommitType.CI: "Changes to CI configuration files and scripts",
            CommitType.CHORE: "Other changes that do not modify src or test files",
            CommitType.REVERT: "Reverts a previous commit",
        }
        return descriptions[self]

    @property
    def emoji(self) -> str:
        emojis = {
            CommitType.FEAT: "✨",
            CommitType.FIX: "🐛",
            CommitType.DOCS: "📚",
            CommitType.STYLE: "💎",
            CommitType.REFACTOR: "♻️",
            CommitType.PERF: "⚡",
            CommitType.TEST: "🧪",
            CommitType.BUILD: "📦",
            CommitType.CI: "🔧",
            CommitType.CHORE: "🔨",
            CommitType.REVERT: "⏪",
        }
        return emojis[self]

    @property
    def label(self) -> str:
        labels = {
            CommitType.FEAT: "Features",
            CommitType.FIX: "Bug Fixes",
            CommitType.DOCS: "Documentation",
            CommitType.STYLE: "Styles",
            CommitType.REFACTOR: "Code Refactoring",
            CommitType.PERF: "Performance Improvements",
            CommitType.TEST: "Tests",
            CommitType.BUILD: "Build System",
            CommitType.CI: "Continuous Integration",
            CommitType.CHORE: "Chores",
            CommitType.REVERT: "Reverts",
        }
        return labels[self]

    @classmethod
    def values(cls) -> list[str]:
        return [t.value for t in cls]

    @classmethod
    def to_prompt_description(cls) -> str:
        return "\n".join(f"- {t.value}: {t.description}" for t in cls)
