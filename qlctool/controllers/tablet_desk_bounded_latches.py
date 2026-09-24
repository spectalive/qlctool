"""The tablet's verified bursts: latched, but ended by the master on their own.

Since 2026-09-13 the tablet may fire an isolated, self-ending burst of the
vertical fog column (`valid_desk_bursts`); that is the one latch the
held-column rule allows, and only a show with the desk has one.
"""

from ..checks.rule_context import RuleContext
from ..checks.valid_desk_bursts import valid_desk_bursts


def tablet_desk_bounded_latches(context: RuleContext) -> frozenset[int]:
    """The burst chasers `rule_held_column` must not report."""
    return frozenset(valid_desk_bursts(context.graph, context.root))
