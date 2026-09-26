"""The rules that read what the console's bindings press.

A key, a pad channel or an audio bar presses buttons without anybody looking
at them: an audio bar must press nothing it should not and must be bound to
something (`audio_triggers`), and a key that holds colour must reach the whole
room (`bank_key_coverage`). Run together, in that order.
"""

from lxml import etree

from .finding import Finding
from .rule_audio_triggers import check_audio_triggers
from .rule_bank_key_coverage import check_bank_key_coverage
from .show_graph import ShowGraph


def key_binding_findings(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    root: etree._Element,
    states: set[int],
) -> list[Finding]:
    """Every binding rule's findings, audio bars first."""
    return [
        *check_audio_triggers(graph, groups, root),
        *check_bank_key_coverage(graph, groups, root, states),
    ]
