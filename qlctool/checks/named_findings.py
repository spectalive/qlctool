"""Findings said in the workspace's language (ruling B10).

The one place a finding's rule name and message are rendered: the rules report
identifiers, and the words follow the language the workspace was generated in,
so an English show's findings read in English end to end.
"""

from dataclasses import replace

from lxml import etree

from ..names.names import Names
from ..names.shipped_names import shipped_names
from ..names.workspace_language import workspace_language
from .display_name_of_rule import display_name_of_rule
from .finding import Finding
from .phrase import Phrase
from .rendered_value import rendered_value


def named_findings(
    findings: list[Finding], root: etree._Element, names: Names | None = None
) -> list[Finding]:
    """Each finding with `rule` and `message` from the workspace's catalogue.

    `names` is the show's own vocabulary, overrides included, when the caller
    has its description: the workspace records its language but not the words
    a description renamed, so without it a renamed `full_white` would still
    read as the shipped name in a message (2026-09-26).
    """
    names = shipped_names(workspace_language(root)) if names is None else names
    language = names.language
    return [
        replace(
            f,
            rule=display_name_of_rule(f.rule_id, language) or f.rule or f.rule_id,
            message=(
                str(rendered_value(names, Phrase(f.message_id, f.fields)))
                if f.message_id
                else f.message
            ),
        )
        for f in findings
    ]
