"""Tests for AI prompt builders."""

from git_ai.agents.prompts import build_changelog_prompt, build_commit_prompt


class TestBuildCommitPrompt:
    def test_contains_conventional_commits_types(self) -> None:
        prompt = build_commit_prompt("diff content")
        assert "feat:" in prompt
        assert "fix:" in prompt

    def test_includes_diff_content(self) -> None:
        prompt = build_commit_prompt("my-diff-content")
        assert "my-diff-content" in prompt

    def test_english_language_instruction(self) -> None:
        prompt = build_commit_prompt("diff", language="en")
        assert "Write the description and body in English" in prompt

    def test_portuguese_language_instruction(self) -> None:
        prompt = build_commit_prompt("diff", language="pt-BR")
        assert "Brazilian Portuguese" in prompt
        assert "type and scope MUST remain in English" in prompt

    def test_includes_allowed_scopes(self) -> None:
        prompt = build_commit_prompt("diff", allowed_scopes=["auth", "api"])
        assert "auth, api" in prompt
        assert "scope MUST be one of" in prompt

    def test_no_scope_restriction_when_empty(self) -> None:
        prompt = build_commit_prompt("diff", allowed_scopes=[])
        assert "Choose an appropriate scope" in prompt

    def test_includes_allowed_types(self) -> None:
        prompt = build_commit_prompt("diff", allowed_types=["feat", "fix"])
        assert "feat, fix" in prompt
        assert "Only use these commit types" in prompt

    def test_auto_body_instruction(self) -> None:
        prompt = build_commit_prompt("diff", body_preference="auto")
        assert "SHOULD explain" in prompt

    def test_always_body_instruction(self) -> None:
        prompt = build_commit_prompt("diff", body_preference="always")
        assert "MUST always be provided" in prompt

    def test_json_schema_in_prompt(self) -> None:
        prompt = build_commit_prompt("diff")
        assert '"type"' in prompt
        assert '"scope"' in prompt
        assert '"description"' in prompt
        assert '"is_breaking_change"' in prompt


class TestBuildChangelogPrompt:
    def test_contains_commits_prompt(self) -> None:
        prompt = build_changelog_prompt("## feat\n- add feature\n")
        assert "add feature" in prompt

    def test_english_language(self) -> None:
        prompt = build_changelog_prompt("commits", language="en")
        assert "Write in English" in prompt

    def test_other_language(self) -> None:
        prompt = build_changelog_prompt("commits", language="pt-BR")
        assert "pt-BR" in prompt
        assert "Keep technical terms in English" in prompt

    def test_json_schema_in_prompt(self) -> None:
        prompt = build_changelog_prompt("commits")
        assert '"sections"' in prompt
        assert '"entries"' in prompt
