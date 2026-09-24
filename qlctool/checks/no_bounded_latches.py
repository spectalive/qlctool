"""A rule provider that vouches for no latched button: the default."""

from .rule_context import RuleContext


def no_bounded_latches(context: RuleContext) -> frozenset[int]:
    """No function is exempt from the held-column rule."""
    return frozenset()
