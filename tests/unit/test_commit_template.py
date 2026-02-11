"""Tests for CommitTemplate value object."""

import pytest

from git_ai.config import GitAiConfig
from git_ai.support.commit_template import CommitTemplate


class TestCommitTemplate:
    def test_default_values(self) -> None:
        tmpl = CommitTemplate()
        assert tmpl.body == "auto"
        assert tmpl.breaking_change_footer is True
        assert tmpl.co_authored_by is False
        assert tmpl.footer_lines == []

    def test_custom_values(self) -> None:
        tmpl = CommitTemplate(
            body="always",
            breaking_change_footer=False,
            co_authored_by=True,
            footer_lines=["Signed-off-by: Test"],
        )
        assert tmpl.body == "always"
        assert tmpl.breaking_change_footer is False
        assert tmpl.co_authored_by is True
        assert tmpl.footer_lines == ["Signed-off-by: Test"]

    def test_raises_for_invalid_body(self) -> None:
        with pytest.raises(ValueError, match="Invalid body preference"):
            CommitTemplate(body="invalid")

    @pytest.mark.parametrize("body", ["auto", "always", "never"])
    def test_accepts_valid_body_preferences(self, body: str) -> None:
        tmpl = CommitTemplate(body=body)
        assert tmpl.body == body

    def test_resolve_minimal_template(self) -> None:
        config = GitAiConfig()
        tmpl = CommitTemplate.resolve("minimal", config)
        assert tmpl.body == "never"
        assert tmpl.breaking_change_footer is False

    def test_resolve_detailed_template(self) -> None:
        config = GitAiConfig()
        tmpl = CommitTemplate.resolve("detailed", config)
        assert tmpl.body == "always"
        assert tmpl.breaking_change_footer is True

    def test_resolve_from_commit_config_when_no_template(self) -> None:
        config = GitAiConfig()
        tmpl = CommitTemplate.resolve(None, config)
        assert tmpl.body == "auto"

    def test_resolve_raises_for_unknown_template(self) -> None:
        config = GitAiConfig()
        with pytest.raises(ValueError, match="Unknown commit template"):
            CommitTemplate.resolve("nonexistent", config)

    def test_error_message_includes_available_templates(self) -> None:
        config = GitAiConfig()
        with pytest.raises(ValueError, match="minimal"):
            CommitTemplate.resolve("nonexistent", config)

    def test_with_overrides_body(self) -> None:
        tmpl = CommitTemplate(body="auto")
        overridden = tmpl.with_overrides(body="never")
        assert overridden.body == "never"
        assert tmpl.body == "auto"  # Original unchanged

    def test_with_overrides_footer(self) -> None:
        tmpl = CommitTemplate(footer_lines=["Line 1"])
        overridden = tmpl.with_overrides(extra_footer_lines=["Line 2"])
        assert overridden.footer_lines == ["Line 1", "Line 2"]

    def test_with_overrides_preserves_other_fields(self) -> None:
        tmpl = CommitTemplate(co_authored_by=True, breaking_change_footer=False)
        overridden = tmpl.with_overrides(body="never")
        assert overridden.co_authored_by is True
        assert overridden.breaking_change_footer is False

    def test_from_dict_with_all_fields(self) -> None:
        data = {
            "body": "always",
            "footer": {
                "breaking_change": False,
                "co_authored_by": True,
                "lines": ["Signed-off-by: Team"],
            },
        }
        tmpl = CommitTemplate.from_dict(data)
        assert tmpl.body == "always"
        assert tmpl.breaking_change_footer is False
        assert tmpl.co_authored_by is True
        assert tmpl.footer_lines == ["Signed-off-by: Team"]

    def test_from_dict_with_defaults(self) -> None:
        tmpl = CommitTemplate.from_dict({})
        assert tmpl.body == "auto"
        assert tmpl.breaking_change_footer is True

    def test_resolve_custom_preset(self) -> None:
        config = GitAiConfig(
            templates={"default": None, "presets": {"my-team": {"body": "always"}}}
        )
        tmpl = CommitTemplate.resolve("my-team", config)
        assert tmpl.body == "always"

    def test_resolve_default_template_from_config(self) -> None:
        config = GitAiConfig(templates={"default": "minimal", "presets": {}})
        tmpl = CommitTemplate.resolve(None, config)
        assert tmpl.body == "never"
