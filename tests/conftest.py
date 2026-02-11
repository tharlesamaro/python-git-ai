"""Shared fixtures for Git AI tests."""

import subprocess
from pathlib import Path

import pytest

from git_ai.config import GitAiConfig
from git_ai.services.git_service import GitService


@pytest.fixture
def config() -> GitAiConfig:
    """Default test configuration."""
    return GitAiConfig()


@pytest.fixture
def tmp_git_repo(tmp_path: Path) -> Path:
    """Create a temporary git repository with an initial commit."""
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=tmp_path,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=tmp_path,
        capture_output=True,
    )
    # Create initial commit
    readme = tmp_path / "README.md"
    readme.write_text("# Test\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "chore: initial commit"],
        cwd=tmp_path,
        capture_output=True,
    )
    return tmp_path


@pytest.fixture
def git_service(tmp_git_repo: Path) -> GitService:
    """GitService backed by a temporary repository."""
    return GitService(working_directory=str(tmp_git_repo))
