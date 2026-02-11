"""Tests for configuration management."""

from pathlib import Path

import pytest

from git_ai.config import GitAiConfig, find_config_file, load_config


class TestGitAiConfig:
    def test_default_values(self) -> None:
        config = GitAiConfig()
        assert config.provider == "anthropic"
        assert config.model is None
        assert config.language == "en"
        assert config.scopes == []
        assert config.types == []
        assert config.max_diff_size == 15000

    def test_default_commit_config(self) -> None:
        config = GitAiConfig()
        assert config.commit.body == "auto"
        assert config.commit.footer.breaking_change is True
        assert config.commit.footer.co_authored_by is False
        assert config.commit.footer.lines == []

    def test_default_changelog_config(self) -> None:
        config = GitAiConfig()
        assert config.changelog.path == "CHANGELOG.md"
        assert config.changelog.with_emojis is True

    def test_default_hook_config(self) -> None:
        config = GitAiConfig()
        assert config.hook.enabled is False
        assert config.hook.strict is True


class TestFindConfigFile:
    def test_finds_config_in_current_dir(self, tmp_path: Path) -> None:
        config_file = tmp_path / ".git-ai.toml"
        config_file.write_text('[git-ai]\nprovider = "openai"\n')
        result = find_config_file(str(tmp_path))
        assert result == config_file

    def test_returns_none_when_no_config(self, tmp_path: Path) -> None:
        result = find_config_file(str(tmp_path))
        assert result is None

    def test_walks_up_directory_tree(self, tmp_path: Path) -> None:
        config_file = tmp_path / ".git-ai.toml"
        config_file.write_text('[git-ai]\nprovider = "openai"\n')
        child = tmp_path / "subdir" / "deep"
        child.mkdir(parents=True)
        result = find_config_file(str(child))
        assert result == config_file


class TestLoadConfig:
    def test_loads_from_toml_file(self, tmp_path: Path) -> None:
        config_file = tmp_path / ".git-ai.toml"
        config_file.write_text(
            '[git-ai]\nprovider = "openai"\nlanguage = "pt-BR"\nmax_diff_size = 10000\n'
        )
        config = load_config(str(tmp_path))
        assert config.provider == "openai"
        assert config.language == "pt-BR"
        assert config.max_diff_size == 10000

    def test_env_override_provider(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GIT_AI_PROVIDER", "claude-code")
        config = load_config(str(tmp_path))
        assert config.provider == "claude-code"

    def test_env_override_language(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GIT_AI_LANGUAGE", "es")
        config = load_config(str(tmp_path))
        assert config.language == "es"

    def test_env_overrides_file(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        config_file = tmp_path / ".git-ai.toml"
        config_file.write_text('[git-ai]\nprovider = "openai"\n')
        monkeypatch.setenv("GIT_AI_PROVIDER", "anthropic")
        config = load_config(str(tmp_path))
        assert config.provider == "anthropic"

    def test_returns_defaults_when_no_config(self, tmp_path: Path) -> None:
        config = load_config(str(tmp_path))
        assert config.provider == "anthropic"
        assert config.language == "en"
