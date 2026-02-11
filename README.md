# Git AI for Python

> 🤖 AI-powered Git workflow automation for Python: Smart commit messages, changelog generation, and commit validation using Conventional Commits.

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Git AI** leverages AI (Anthropic Claude or OpenAI GPT) to automate your Git workflow.

## Features

- 📝 **Smart Commit Messages**: Generate meaningful commits following Conventional Commits
- 📊 **Automated Changelogs**: Create beautiful changelogs from commit history
- ✅ **Commit Validation**: Ensure all commits follow Conventional Commits spec
- 🌍 **Multi-language**: EN, PT-BR, ES, FR, DE, IT, JA, KO, ZH
- 🎯 **Customizable**: Configure types and scopes for your project

## Installation

```bash
# Using UV (recommended)
uv tool install git-ai

# Using pip
pip install git-ai

# Using pipx
pipx install git-ai
```

## Quick Start

1. Set up your API key:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
# or
export OPENAI_API_KEY=sk-...
```

2. Initialize:
```bash
git-ai setup
```

3. Use it:
```bash
git add .
git-ai commit
```

## Commands

### `git-ai commit`
Generate AI-powered commit messages.

```bash
git-ai commit [OPTIONS]

Options:
  -a, --all    Stage all changes before committing
```

### `git-ai changelog`
Generate changelog from commits.

```bash
git-ai changelog [OPTIONS]

Options:
  --from TEXT   Starting reference
  --to TEXT     Ending reference (default: HEAD)
  --tag TEXT    Version tag
  --dry-run     Preview only
```

### `git-ai setup`
Interactive configuration wizard.

## Configuration

`.git-ai.toml`:
```toml
[git-ai]
provider = "anthropic"
language = "en"
max_diff_size = 15000

[git-ai.changelog]
path = "CHANGELOG.md"
with_emojis = true
```

## Development

```bash
# Clone and setup
git clone https://github.com/tharlesamaro/python-git-ai.git
cd python-git-ai
uv sync

# Run tests
uv run pytest

# Format and lint
uv run black src
uv run ruff check src
```

## License

MIT License - see [LICENSE](LICENSE)

---

Made with ❤️ by [Tharles Amaro](https://github.com/tharlesamaro)

[🇧🇷 Leia em Português](README.pt-BR.md)
