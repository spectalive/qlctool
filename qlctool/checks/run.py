"""Run every check over a workspace and return what is wrong with the show.

This is the answer to a show that worked by luck. QLC+'s own validation says
the file loads; these say the room will do what the buttons promise - that
nothing lit is dark, that no two programmes are writing the same colour, that
the fixtures without RGB were not silently skipped, and that the console cannot
be pressed into a state the show was never built for.

Every rule here exists because something went wrong in a real room. Adding one
is how a bug stops being able to happen twice.
"""

from lxml import etree

from ..capabilities_of import capabilities_of
from ..library import FixtureLibrary
from ..workspace import Workspace
from .console_states import room_states
from .entry_points import entry_points
from .finding import ERROR, Finding
from .rule_collision import check_collisions
from .rule_console import check_console
from .rule_intensity import check_intensity
from .rule_smoke import check_smoke
from .rule_strobe_in_cycle import check_strobe_in_cycle
from .rule_unfinished_effect import check_unfinished_effects
from .rule_wheel_colour import check_wheel_colour
from .show_graph import build_show_graph, group_fixtures

DEFAULT_CANVAS = (1440, 900)


def check_workspace(
    workspace: Workspace,
    library: FixtureLibrary,
    canvas: tuple[int, int] | None = None,
) -> list[Finding]:
    """Every finding, worst first, in the order a person would fix them."""
    root = workspace.root
    capabilities = capabilities_of(root, library)
    graph = build_show_graph(root, capabilities)
    groups = group_fixtures(root)
    entries = entry_points(root)
    states = room_states(root, graph, groups)

    findings: list[Finding] = []
    findings += check_intensity(graph, groups, entries, states)
    findings += check_wheel_colour(graph, groups, entries)
    findings += check_collisions(graph, groups, entries)
    findings += check_unfinished_effects(graph, groups, entries)
    findings += check_strobe_in_cycle(graph, groups, entries)
    findings += check_smoke(graph, groups, entries)
    findings += check_console(graph, root, canvas or _canvas(root))
    return sorted(findings, key=lambda f: (f.severity != ERROR, f.rule, f.function))


def _canvas(root: etree._Element) -> tuple[int, int]:
    from ..xmlutil import find_local

    console = find_local(root, "VirtualConsole")
    properties = find_local(console, "Properties") if console is not None else None
    size = find_local(properties, "Size") if properties is not None else None
    if size is None:
        return DEFAULT_CANVAS
    return int(size.attrib.get("Width", DEFAULT_CANVAS[0])), int(
        size.attrib.get("Height", DEFAULT_CANVAS[1])
    )
