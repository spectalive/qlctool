"""Findings named in the workspace's language and put in the order a person fixes them.

The one place a rule's display name is rendered (ruling B10, 2026-09-25): the
rules report an identifier, and the name follows the language the workspace
was generated in, so an English show's findings read in English.
"""

from dataclasses import replace

from lxml import etree

from ..names.workspace_language import workspace_language
from .finding import ERROR, Finding
from .rule_display_name import rule_display_name


def named_in_order(findings: list[Finding], root: etree._Element) -> list[Finding]:
    """Errors first, then by rule name and function, each named from the catalogue."""
    language = workspace_language(root)
    named = [
        replace(f, rule=rule_display_name(f.rule_id, language) or f.rule or f.rule_id)
        for f in findings
    ]
    return sorted(named, key=lambda f: (f.severity != ERROR, f.rule, f.function))
