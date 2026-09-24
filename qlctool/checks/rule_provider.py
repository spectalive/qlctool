"""A set of checks that belongs to one part of a show: a controller, or a show's own."""

from collections.abc import Callable
from dataclasses import dataclass

from lxml import etree

from .finding import Finding
from .rule_context import RuleContext


@dataclass(frozen=True)
class RuleProvider:
    """`applies` says whether the workspace uses this part at all; `check` runs its rules."""

    name: str
    applies: Callable[[etree._Element], bool]
    check: Callable[[RuleContext], list[Finding]]
