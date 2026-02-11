"""Prompt builders for AI agents."""

from git_ai.enums import CommitType

LANGUAGE_NAMES: dict[str, str] = {
    "pt-BR": "Brazilian Portuguese",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
}


def _build_language_instruction(language: str) -> str:
    if language == "en":
        return "8. Write the description and body in English."
    name = LANGUAGE_NAMES.get(language, language)
    return (
        f"8. Write the description and body in {name}. The type and scope MUST remain in English."
    )


def _build_scope_instruction(allowed_scopes: list[str]) -> str:
    if not allowed_scopes:
        return "9. Choose an appropriate scope based on the files changed, or leave it empty if not applicable."
    scopes_list = ", ".join(allowed_scopes)
    return f"9. The scope MUST be one of: {scopes_list}. If none fits, leave the scope empty."


def _build_types_instruction(allowed_types: list[str]) -> str:
    if not allowed_types:
        return ""
    types_list = ", ".join(allowed_types)
    return f"10. Only use these commit types: {types_list}."


def _build_body_instruction(body_preference: str) -> str:
    if body_preference == "always":
        return "3. The `body` MUST always be provided. Explain WHAT changed and WHY (not HOW). Never leave it empty."
    return "3. The `body` SHOULD explain WHAT changed and WHY (not HOW). Leave empty if the description is self-explanatory."


def build_commit_prompt(
    diff: str,
    language: str = "en",
    allowed_scopes: list[str] | None = None,
    allowed_types: list[str] | None = None,
    body_preference: str = "auto",
) -> str:
    """Build the full prompt for commit message generation."""
    types_description = CommitType.to_prompt_description()
    language_instruction = _build_language_instruction(language)
    scope_instruction = _build_scope_instruction(allowed_scopes or [])
    types_instruction = _build_types_instruction(allowed_types or [])
    body_instruction = _build_body_instruction(body_preference)

    return f"""You are a Git commit message expert that strictly follows the Conventional Commits specification (v1.0.0).

Your task is to analyze a git diff and generate a precise, descriptive commit message.

## Conventional Commits Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

## Available commit types:
{types_description}

## Rules:
1. The `type` MUST be one of the types listed above.
2. The `description` MUST be a short summary of the code changes (imperative mood, lowercase, no period at the end).
{body_instruction}
4. Set `is_breaking_change` to true ONLY if the changes break backward compatibility.
5. Analyze the diff carefully to determine the most accurate type.
6. If multiple changes are present, focus on the primary change for the type.
7. Keep the description under 72 characters.
{scope_instruction}
{types_instruction}
{language_instruction}

You MUST respond with ONLY a valid JSON object (no markdown, no code fences, no extra text).
Use this exact structure:
{{
    "type": "string",
    "scope": "string or empty string",
    "description": "string",
    "body": "string or empty string",
    "is_breaking_change": false
}}

Analyze this git diff and generate a commit message:

```diff
{diff}
```"""


def build_changelog_prompt(
    commits_prompt: str,
    language: str = "en",
) -> str:
    """Build the full prompt for changelog generation."""
    if language == "en":
        language_instruction = "Write in English."
    else:
        language_instruction = f"Write in the language identified by the code: {language}. Keep technical terms in English."

    return f"""You are a changelog writer. You receive a list of git commits grouped by type and generate a clean, human-readable changelog.

## Rules:
1. For each commit, write a concise, user-friendly description of what changed.
2. Focus on the impact for the end user or developer, not implementation details.
3. Remove redundant or duplicate entries.
4. Keep each entry to a single line.
5. Do NOT include commit hashes, author names, or dates in the entries.
6. If a scope is present, keep it as a prefix in parentheses.
7. {language_instruction}

You MUST respond with ONLY a valid JSON object (no markdown, no code fences, no extra text).
Use this exact structure:
{{
    "sections": [
        {{
            "type": "feat",
            "entries": ["Description of change 1", "Description of change 2"]
        }}
    ]
}}

{commits_prompt}"""
