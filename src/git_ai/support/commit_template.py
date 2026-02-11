"""Value object that resolves and holds commit template settings."""

from dataclasses import dataclass, field
from typing import Any, Self


@dataclass(frozen=True)
class CommitTemplate:
    """
    Templates bundle body + footer preferences into named presets.
    Resolution: command flag > config default > raw commit config.
    """

    body: str = "auto"
    breaking_change_footer: bool = True
    co_authored_by: bool = False
    footer_lines: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.body not in ("auto", "always", "never"):
            raise ValueError(
                f"Invalid body preference: '{self.body}'. Must be 'auto', 'always', or 'never'."
            )

    @classmethod
    def resolve(cls, template_name: str | None, config: Any) -> Self:
        """
        Resolve a CommitTemplate from the given template name.
        Built-in templates 'minimal' and 'detailed' are always available.
        """
        if template_name is None:
            template_name = config.templates.default

        if template_name is None:
            return cls.from_commit_config(config)

        built_in = cls._built_in_templates()
        if template_name in built_in:
            return built_in[template_name]

        presets = config.templates.presets
        if template_name in presets:
            return cls.from_dict(presets[template_name])

        available = list(built_in.keys()) + list(presets.keys())
        raise ValueError(
            f"Unknown commit template: '{template_name}'. Available: {', '.join(available)}"
        )

    @classmethod
    def from_commit_config(cls, config: Any) -> Self:
        """Build from the commit config section (no template)."""
        return cls(
            body=config.commit.body,
            breaking_change_footer=config.commit.footer.breaking_change,
            co_authored_by=config.commit.footer.co_authored_by,
            footer_lines=list(config.commit.footer.lines),
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Build from a dict (template preset definition)."""
        footer = data.get("footer", {})
        return cls(
            body=data.get("body", "auto"),
            breaking_change_footer=footer.get("breaking_change", True),
            co_authored_by=footer.get("co_authored_by", False),
            footer_lines=list(footer.get("lines", [])),
        )

    def with_overrides(
        self,
        body: str | None = None,
        extra_footer_lines: list[str] | None = None,
    ) -> Self:
        """Return a new instance with overrides applied."""
        return CommitTemplate(
            body=body or self.body,
            breaking_change_footer=self.breaking_change_footer,
            co_authored_by=self.co_authored_by,
            footer_lines=self.footer_lines + (extra_footer_lines or []),
        )

    @staticmethod
    def _built_in_templates() -> "dict[str, CommitTemplate]":
        return {
            "minimal": CommitTemplate(
                body="never",
                breaking_change_footer=False,
                co_authored_by=False,
                footer_lines=[],
            ),
            "detailed": CommitTemplate(
                body="always",
                breaking_change_footer=True,
                co_authored_by=False,
                footer_lines=[],
            ),
        }
