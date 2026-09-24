"""The tablet desk's rules over one workspace."""

from ..checks.finding import Finding
from ..checks.rule_context import RuleContext
from ..checks.rule_desk_bursts import check_desk_bursts


def tablet_desk_check(context: RuleContext) -> list[Finding]:
    """Every held accent has one verified, bounded burst (2026-09-13)."""
    return check_desk_bursts(context.graph, context.root)
