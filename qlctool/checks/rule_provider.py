"""A set of checks that belongs to one part of a show: a controller, or a show's own."""

from collections.abc import Callable
from dataclasses import dataclass

from lxml import etree

from .finding import Finding
from .no_bounded_latches import no_bounded_latches
from .rule_context import RuleContext


@dataclass(frozen=True)
class RuleProvider:
    """`applies` says whether the workspace uses this part at all; `check` runs its rules.

    `bounded_latches` names the latched functions this part guarantees to end on
    their own (the tablet's bursts), which `rule_held_column` then allows.
    """

    name: str
    applies: Callable[[etree._Element], bool]
    check: Callable[[RuleContext], list[Finding]]
    bounded_latches: Callable[[RuleContext], frozenset[int]] = no_bounded_latches
