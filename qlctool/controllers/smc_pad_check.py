"""The SMC-PAD's rules over one workspace."""

from ..checks.finding import Finding
from ..checks.rule_context import RuleContext
from ..checks.rule_pad_input import check_pad_input


def smc_pad_check(context: RuleContext) -> list[Finding]:
    """Bindings the pad cannot send, doubled channels, and a missing MIDI input patch."""
    return check_pad_input(context.root)
