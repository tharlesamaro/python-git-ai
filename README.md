# Python Git AI

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**English** | [Portugues](README.pt-BR.md)

AI-powered Git workflow automation for Python. Generate smart commit messages, changelogs, and validate commits using Conventional Commits.

## Why use this tool instead of Claude Code directly?

If you already use Claude Code CLI, you might wonder: "Why not just ask Claude to commit for me?" Here's what this tool brings to the table:

| Feature | Claude Code alone | Python Git AI |
|---------|------------------|---------------|
| Conventional Commits format | You have to ask every time | Enforced automatically via structured output |
| Consistent JSON schema | Free-form text, may vary | Validated against a strict schema every time |
| Project-specific scopes | Must remember to mention them | Configured once, enforced on every commit |
| Allowed commit types | Manual discipline | Restricted by config, AI cannot use others |
| Multi-language support | Must specify in every prompt | Configured once, always applied |
| Changelog generation | Manual work | Automated from commit history between tags |
| Git hook validation | Not available | Optional hook rejects non-conventional commits |
| Team consistency | Each developer prompts differently | Same rules for everyone via shared config |
| Max diff size control | No control, may exceed context | Auto-truncated to configured limit |
| Works without CLI installed | N/A | Falls back to API providers (Anthropic/OpenAI) |

In short: this tool turns AI-generated commits into a **repeatable, team-wide standard** instead of a one-off prompt.

## Features

- **`git-ai commit`** -- Generate commit messages from staged changes using AI, following Conventional Commits
- **`git-ai changelog`** -- Generate structured changelogs from commit history between tags
- **`git-ai setup`** -- Interactive configuration wizard
- **3 providers** -- Anthropic API, OpenAI API, or Claude Code CLI (no API key needed)
- **9 languages** -- English, Portuguese, Spanish, French, German, Italian, Japanese, Korean, Chinese
- **Scope enforcement** -- Restrict commits to project-specific scopes
- **Type restriction** -- Limit which Conventional Commits types are allowed
- **Commit templates** -- Built-in (`minimal`, `detailed`) and custom presets for body + footer settings
- **Body control** -- Configure whether AI always includes body, never includes it, or decides automatically
- **Footer control** -- Toggle BREAKING CHANGE footer, add custom footer lines, control Co-Authored-By trailer
- **Git hook** -- Optional `commit-msg` hook to reject non-conventional commits
- **Structured output** -- AI responses are validated against a JSON schema, never free-form text
- **Diff truncation** -- Large diffs are automatically truncated to fit AI context windows

## Requirements

- Python 3.13+
- One of the following:
  - An API key from Anthropic or OpenAI
  - **OR** [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed on your machine (uses your existing Claude subscription, e.g. Max plan -- no API key required)

## Installation

```bash
# Using UV (recommended)
uv tool install git-ai

# Using pip
pip install git-ai

# Using pipx
pipx install git-ai
```

## Provider Setup

### Option 1: Anthropic API (default)

```bash
export GIT_AI_PROVIDER=anthropic
export ANTHROPIC_API_KEY=your-api-key
```

### Option 2: OpenAI API

```bash
export GIT_AI_PROVIDER=openai
export OPENAI_API_KEY=your-api-key
```

### Option 3: Claude Code CLI (no API key)

If you have a Claude subscription (e.g. Max plan) and the Claude Code CLI installed, you can use it directly without any API key:

```bash
export GIT_AI_PROVIDER=claude-code
```

Make sure the `claude` binary is available in your PATH. Install it from: https://docs.anthropic.com/en/docs/claude-code

This option invokes the Claude Code CLI as a subprocess, passing a structured prompt and parsing the JSON response. It consumes from your existing subscription usage -- no separate API tokens needed.

## Usage

### `git-ai commit` -- Generate a commit message

Stage your changes and run:

```bash
git-ai commit
```

Or stage everything automatically with the `--all` (`-a`) flag:

```bash
git-ai commit --all
```

**Available options:**

| Option | Short | Description |
|--------|-------|-------------|
| `--all` | `-a` | Stage all changes before committing |
| `--template` | | Use a named commit template (e.g. `minimal`, `detailed`) |
| `--no-body` | | Strip body from the commit message |
| `--footer` | | Add custom footer line(s) (can be used multiple times) |

**What happens:**

1. Reads your staged diff (truncated if it exceeds `max_diff_size`)
2. Sends it to the configured AI provider
3. Receives a structured response with `type`, `scope`, `description`, `body`, and `is_breaking_change`
4. Validates the type and scope against your config
5. Formats the message following Conventional Commits
6. Lets you choose what to do next

**Interactive menu:**

```
Staged changes:
 src/models/user.py    | 12 ++++++---
 src/api/auth.py       | 8 ++++--
 2 files changed, 14 insertions(+), 6 deletions(-)

Generated commit message:
  feat(auth): add email verification on registration

What would you like to do?
  > accept
    edit
    regenerate
    cancel
```

- **accept** -- Creates the commit with the generated message
- **edit** -- Opens prompts to modify the title and body separately
- **regenerate** -- Calls the AI again for a different message
- **cancel** -- Aborts without committing

**Example with body and breaking change:**

```
Generated commit message:
  feat(api)!: replace REST endpoints with GraphQL

  Migrate all API endpoints from REST to GraphQL.
  This removes all /api/v1/* routes.

  BREAKING CHANGE: replace REST endpoints with GraphQL
```

### `git-ai changelog` -- Generate a changelog

```bash
git-ai changelog
```

**Available options:**

| Option | Description | Default |
|--------|-------------|---------|
| `--from` | Starting tag or commit hash | Latest tag (or first commit if no tags) |
| `--to` | Ending tag or commit hash | `HEAD` |
| `--tag` | Version tag for the changelog header | Interactive prompt |
| `--dry-run` | Preview without writing to file | `false` |

**Examples:**

```bash
# Auto-detect range (latest tag to HEAD)
git-ai changelog

# From a specific tag to HEAD
git-ai changelog --from v1.0.0

# Between two references
git-ai changelog --from v1.0.0 --to v1.1.0

# Specify the version tag upfront
git-ai changelog --tag v2.0.0

# Preview without writing to file
git-ai changelog --dry-run

# Combine options
git-ai changelog --from v1.0.0 --to v2.0.0 --tag v2.0.0 --dry-run
```

**What happens:**

1. Resolves the starting reference (priority: `--from` > latest tag > first commit)
2. Gets all commits between `from` and `to`
3. Parses each commit message using the Conventional Commits format
4. Groups commits by type (`feat`, `fix`, `docs`, etc.)
5. Sends the grouped commits to the AI for human-readable descriptions
6. Formats the output as Markdown with emojis (configurable)
7. Shows a preview and asks for confirmation before writing

**Output example (`CHANGELOG.md`):**

```markdown
## [v1.2.0] - 2026-02-11

### Features

- Add email verification during user registration
- Implement password reset via SMS

### Bug Fixes

- Resolve null pointer when loading user preferences
- Fix timezone handling in scheduled notifications

### Documentation

- Update API authentication guide with OAuth2 examples
```

If `changelog.with_emojis` is enabled (default), section titles include emojis:

```markdown
### ✨ Features
### 🐛 Bug Fixes
### 📚 Documentation
### ♻️ Code Refactoring
### ⚡ Performance Improvements
### 🧪 Tests
### 📦 Build System
### 🔧 Continuous Integration
### 🔨 Chores
### ⏪ Reverts
```

The changelog is prepended to the existing file. If `CHANGELOG.md` already exists, new content is added at the top (below the header), preserving previous entries.

### `git-ai setup` -- Interactive configuration

```bash
git-ai setup
```

The wizard walks you through every configurable option:

1. **AI provider** -- Anthropic API, OpenAI API, or Claude Code CLI
2. **Language** -- English, Portuguese (Brazil), Spanish, French, German, Italian, Japanese, Korean, or Chinese
3. **Scopes** -- Define allowed scopes for your project (e.g., `auth`, `api`, `ui`, `database`)
4. **Types** -- Restrict which commit types are allowed (e.g., only `feat`, `fix`, `docs`)
5. **Body preference** -- How the AI handles commit message body (auto, always, never)
6. **Git hook** -- Install a `commit-msg` hook that rejects non-conventional commits

After setup, it writes `.git-ai.toml` and shows the environment variables you need to set.

## Configuration

All options in `.git-ai.toml`:

```toml
[git-ai]
# AI provider: 'anthropic', 'openai', or 'claude-code'
provider = "anthropic"

# AI model override (empty = provider default)
# Examples: 'claude-sonnet-4-5-20250929', 'gpt-4o', etc.
# model = "claude-sonnet-4-5-20250929"

# Language for commit messages and changelog entries
# Supported: 'en', 'pt-BR', 'es', 'fr', 'de', 'it', 'ja', 'ko', 'zh'
language = "en"

# Allowed commit scopes (empty = any scope allowed)
# The AI will only use scopes from this list
# Example: ["auth", "api", "ui", "database", "config"]
scopes = []

# Allowed commit types (empty = all Conventional Commits types allowed)
# The AI will only use types from this list
# Example: ["feat", "fix", "docs", "refactor", "test"]
types = []

# Maximum diff size sent to the AI (in characters)
# Diffs larger than this are truncated with a warning
max_diff_size = 15000

[git-ai.commit]
# Body behavior: 'auto' (AI decides), 'always' (AI must include), 'never' (stripped from output)
body = "auto"

[git-ai.commit.footer]
# Whether to include the BREAKING CHANGE footer when applicable
breaking_change = true

# Whether to include a "Co-Authored-By" trailer in commit messages
# Set to false to prevent AI attribution lines in commits
co_authored_by = false

# Custom footer lines to append to every commit message
# Example: ["Signed-off-by: Name <email@example.com>"]
lines = []

[git-ai.templates]
# Default template (empty = no template, use 'commit' settings directly)
# default = "minimal"

# Custom template definitions
# [git-ai.templates.presets.my-team]
# body = "always"
# breaking_change = true
# co_authored_by = false
# lines = ["Signed-off-by: Team <team@example.com>"]

[git-ai.changelog]
# File path relative to project root
path = "CHANGELOG.md"

# Include emojis in section titles (e.g., "### ✨ Features")
with_emojis = true

[git-ai.hook]
# Whether the commit-msg validation hook is enabled
enabled = false

# When true, rejects non-conventional commits
# When false, only displays a warning
strict = true
```

### Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GIT_AI_PROVIDER` | AI provider (`anthropic`, `openai`, `claude-code`) | `anthropic` |
| `GIT_AI_MODEL` | AI model override | Provider default |
| `GIT_AI_LANGUAGE` | Commit message language | `en` |
| `GIT_AI_MAX_DIFF_SIZE` | Max diff size in characters | `15000` |
| `GIT_AI_COMMIT_BODY` | Body behavior (`auto`, `always`, `never`) | `auto` |
| `GIT_AI_CO_AUTHORED_BY` | Include Co-Authored-By trailer | `false` |
| `GIT_AI_TEMPLATE` | Default commit template name | -- |
| `ANTHROPIC_API_KEY` | Anthropic API key (when provider is `anthropic`) | -- |
| `OPENAI_API_KEY` | OpenAI API key (when provider is `openai`) | -- |

## Commit Templates

Templates bundle body and footer preferences into named presets. They're entirely optional -- without a template, the `commit` config section is used directly.

### Built-in templates

| Template | Body | BREAKING CHANGE footer | Use case |
|----------|------|----------------------|----------|
| `minimal` | Never | No | Quick, one-line commits |
| `detailed` | Always | Yes | Thorough commits with full context |

### Using templates

```bash
# Use a built-in template
git-ai commit --template minimal

# Override body on the fly
git-ai commit --no-body

# Add custom footers
git-ai commit --footer "Signed-off-by: Name <email>"
git-ai commit --footer "Reviewed-by: Alice" --footer "Tested-by: Bob"

# Combine options
git-ai commit --template detailed --footer "Signed-off-by: Team <team@example.com>"
```

### Set a default template

Via environment variable:

```bash
export GIT_AI_TEMPLATE=minimal
```

Or in `.git-ai.toml`:

```toml
[git-ai.templates]
default = "minimal"
```

### Disabling Co-Authored-By

By default, the `Co-Authored-By` trailer is **not** included in commit messages. If you want to enable it:

```toml
# .git-ai.toml
[git-ai.commit.footer]
co_authored_by = true
```

Or via environment variable:

```bash
export GIT_AI_CO_AUTHORED_BY=true
```

When enabled, commits will include a trailer like:

```
Co-Authored-By: Claude <noreply@anthropic.com>
```

Set it to `false` (default) to keep commits clean without AI attribution.

## Git Hook

The tool includes an optional `commit-msg` git hook that validates commit messages against the Conventional Commits specification.

**What it validates:**

- The message must match the format: `<type>(<scope>): <description>`
- The type must be one of: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`
- The first line must not exceed 72 characters
- Merge commits, reverts, fixups, and squashes are automatically allowed

**Install the hook:**

```bash
# Via the setup wizard
git-ai setup

# Or manually copy the hook file
cp hooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

**Example of a rejected commit:**

```
$ git commit -m "updated stuff"

Invalid commit message format!

Your message:
  updated stuff

Expected format:
  <type>(<scope>): <description>

Valid types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert

Examples:
  feat(auth): add OAuth2 login support
  fix: resolve null pointer in user service
  docs(readme): update installation instructions

Tip: Use 'git-ai commit' to generate valid messages automatically.
```

## Conventional Commits

This tool follows the [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Supported types

| Type | Emoji | Description |
|------|-------|-------------|
| `feat` | ✨ | A new feature |
| `fix` | 🐛 | A bug fix |
| `docs` | 📚 | Documentation only changes |
| `style` | 💎 | Code style changes (formatting, semicolons, etc.) |
| `refactor` | ♻️ | Code refactoring (no feature or fix) |
| `perf` | ⚡ | Performance improvements |
| `test` | 🧪 | Adding or fixing tests |
| `build` | 📦 | Build system or dependency changes |
| `ci` | 🔧 | CI configuration changes |
| `chore` | 🔨 | Other changes (tooling, configs, etc.) |
| `revert` | ⏪ | Reverts a previous commit |

### Breaking changes

Breaking changes are indicated by:

- An `!` after the type/scope: `feat(api)!: remove deprecated endpoints`
- A `BREAKING CHANGE:` footer in the body

The AI detects breaking changes automatically from the diff and sets `is_breaking_change` accordingly.

## Architecture

The tool uses a service abstraction layer (`AiService` contract) that allows swapping between providers without changing command logic:

- **`AnthropicAiService`** -- Uses the Anthropic SDK with structured output for the Anthropic API
- **`OpenAiService`** -- Uses the OpenAI SDK for OpenAI API
- **`ClaudeCodeAiService`** -- Invokes the `claude` CLI as a subprocess for users with a Claude subscription

The provider is resolved at runtime based on the `provider` setting in `.git-ai.toml`. All implementations return the same structured dict format, ensuring consistent behavior regardless of the provider.

## Development

```bash
# Clone and setup
git clone https://github.com/tharlesamaro/python-git-ai.git
cd python-git-ai
uv sync

# Run tests
uv run pytest

# Format and lint
uv run ruff format src tests
uv run ruff check src tests

# Type checking
uv run mypy src

# Run tests with Docker
docker compose run --rm test
```

## Contributing

Contributions are welcome! Please follow Conventional Commits for your commit messages.

1. Fork the repository
2. Create your feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git-ai commit`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

## License

The MIT License (MIT). See [LICENSE](LICENSE) for details.
