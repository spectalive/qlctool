"""The rules that read what a held Flash button does to the rig.

A Flash button is the one widget whose scene lives exactly as long as a finger:
it must be a Scene (`flash_scene`), it must strobe (`flash_strobe`) at the top
of the strobe's run (`flash_speed`), and when it lights the whole rig it must
light the smoke columns too (`flash_lit_smoke`). Its strobe must not be
out-bid by the level beneath (`strobe_masked_by_htp`), and forced LTP it must
not zero what another button gives (`flash_forced_zero`). Run together, in
that order.
"""

from lxml import etree

from .finding import Finding
from .rule_flash_forced_zero import check_flash_forced_zero
from .rule_flash_lit_smoke import check_flash_lit_smoke
from .rule_flash_scene import check_flash_scene
from .rule_flash_speed import check_flash_speed
from .rule_flash_strobe import check_flash_strobe
from .rule_strobe_masked_by_htp import check_strobe_masked_by_htp
from .show_graph import ShowGraph


def flash_button_findings(
    graph: ShowGraph,
    groups: dict[int, tuple[int, ...]],
    root: etree._Element,
    states: set[int],
    entries: dict[int, str],
) -> list[Finding]:
    """Every Flash-button rule's findings, in the order check_workspace ran them."""
    return [
        *check_flash_scene(graph, root),
        *check_flash_strobe(graph, groups, root),
        *check_flash_speed(graph, groups, root),
        *check_flash_lit_smoke(graph, groups, root),
        *check_strobe_masked_by_htp(graph, groups, root, states, entries),
        *check_flash_forced_zero(graph, groups, root, entries),
    ]
