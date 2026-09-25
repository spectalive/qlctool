"""The rule providers whose controller is in the workspace being checked."""

from collections.abc import Sequence

from lxml import etree

from .rule_provider import RuleProvider
from .rule_providers import rule_providers


def applying_providers(
    root: etree._Element, providers: Sequence[RuleProvider] | None = None
) -> list[RuleProvider]:
    """The installed providers, or `providers` when given, that apply to `root`."""
    return [p for p in (rule_providers() if providers is None else providers) if p.applies(root)]
