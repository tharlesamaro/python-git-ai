"""Configuration management for Git AI using .git-ai.toml."""

import os
import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class FooterConfig(BaseModel):
    breaking_change: bool = True
    co_authored_by: bool = False
    lines: list[str] = Field(default_factory=list)


class CommitConfig(BaseModel):
    body: str = "auto"
    footer: FooterConfig = Field(default_factory=FooterConfig)


class TemplatesConfig(BaseModel):
    default: str | None = None
    presets: dict[str, dict[str, Any]] = Field(default_factory=dict)


class ChangelogConfig(BaseModel):
    path: str = "CHANGELOG.md"
    with_emojis: bool = True


class HookConfig(BaseModel):
    enabled: bool = False
    strict: bool = True


class GitAiConfig(BaseModel):
    provider: str = "anthropic"
    model: str | None = None
    language: str = "en"
    scopes: list[str] = Field(default_factory=list)
    types: list[str] = Field(default_factory=list)
    max_diff_size: int = 15000
    commit: CommitConfig = Field(default_factory=CommitConfig)
    templates: TemplatesConfig = Field(default_factory=TemplatesConfig)
    changelog: ChangelogConfig = Field(default_factory=ChangelogConfig)
    hook: HookConfig = Field(default_factory=HookConfig)


def find_config_file(start_dir: str | None = None) -> Path | None:
    """Find .git-ai.toml by walking up from start_dir to root."""
    current = Path(start_dir or os.getcwd()).resolve()
    while True:
        config_path = current / ".git-ai.toml"
        if config_path.is_file():
            return config_path
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def load_config(start_dir: str | None = None) -> GitAiConfig:
    """Load configuration from .git-ai.toml and environment variables."""
    config_path = find_config_file(start_dir)
    file_data: dict[str, Any] = {}

    if config_path is not None:
        with open(config_path, "rb") as f:
            raw = tomllib.load(f)
        file_data = raw.get("git-ai", {})

    # Environment variable overrides
    env_overrides: dict[str, Any] = {}

    if val := os.environ.get("GIT_AI_PROVIDER"):
        env_overrides["provider"] = val
    if val := os.environ.get("GIT_AI_MODEL"):
        env_overrides["model"] = val
    if val := os.environ.get("GIT_AI_LANGUAGE"):
        env_overrides["language"] = val
    if val := os.environ.get("GIT_AI_MAX_DIFF_SIZE"):
        env_overrides["max_diff_size"] = int(val)
    if val := os.environ.get("GIT_AI_COMMIT_BODY"):
        env_overrides.setdefault("commit", {})["body"] = val
    if val := os.environ.get("GIT_AI_CO_AUTHORED_BY"):
        env_overrides.setdefault("commit", {}).setdefault("footer", {})["co_authored_by"] = (
            val.lower() in ("true", "1", "yes")
        )
    if val := os.environ.get("GIT_AI_TEMPLATE"):
        env_overrides.setdefault("templates", {})["default"] = val

    # Merge: file data + env overrides
    merged = _deep_merge(file_data, env_overrides)

    return GitAiConfig(**merged)


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries, with override taking precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
