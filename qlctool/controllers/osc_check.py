"""The OSC surface's rules over one workspace."""

from ..checks.finding import Finding
from ..checks.rule_context import RuleContext
from ..checks.rule_osc_input import check_osc_input


def osc_check(context: RuleContext) -> list[Finding]:
    """Controls sharing an OSC channel."""
    return check_osc_input(context.root)
