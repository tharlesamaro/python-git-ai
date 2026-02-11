"""Tests for CommitType enum."""

import pytest

from git_ai.enums.commit_type import CommitType


class TestCommitType:
    def test_has_all_conventional_commit_types(self) -> None:
        expected = {
            "feat",
            "fix",
            "docs",
            "style",
            "refactor",
            "perf",
            "test",
            "build",
            "ci",
            "chore",
            "revert",
        }
        assert set(CommitType.values()) == expected

    def test_returns_correct_description_for_feat(self) -> None:
        assert CommitType.FEAT.description == "A new feature"

    def test_returns_correct_description_for_fix(self) -> None:
        assert CommitType.FIX.description == "A bug fix"

    def test_returns_correct_emoji_for_feat(self) -> None:
        assert CommitType.FEAT.emoji == "✨"

    def test_returns_correct_emoji_for_fix(self) -> None:
        assert CommitType.FIX.emoji == "🐛"

    def test_returns_correct_label_for_feat(self) -> None:
        assert CommitType.FEAT.label == "Features"

    def test_returns_correct_label_for_fix(self) -> None:
        assert CommitType.FIX.label == "Bug Fixes"

    def test_all_types_have_descriptions(self) -> None:
        for ct in CommitType:
            assert ct.description, f"{ct.value} should have a description"

    def test_all_types_have_emojis(self) -> None:
        for ct in CommitType:
            assert ct.emoji, f"{ct.value} should have an emoji"

    def test_all_types_have_labels(self) -> None:
        for ct in CommitType:
            assert ct.label, f"{ct.value} should have a label"

    def test_can_be_created_from_valid_string(self) -> None:
        assert CommitType("feat") is CommitType.FEAT
        assert CommitType("fix") is CommitType.FIX

    def test_raises_for_invalid_string(self) -> None:
        with pytest.raises(ValueError):
            CommitType("invalid")

    def test_values_returns_all_string_values(self) -> None:
        values = CommitType.values()
        assert len(values) == 11
        assert "feat" in values

    def test_to_prompt_description_contains_all_types(self) -> None:
        description = CommitType.to_prompt_description()
        for ct in CommitType:
            assert f"- {ct.value}:" in description
