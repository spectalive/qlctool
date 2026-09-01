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
from .rule_accent_restore import check_accent_restore
from .rule_audio_triggers import check_audio_triggers
from .rule_collision import check_collisions
from .rule_colour_clocks import check_colour_clocks
from .rule_console import check_console
from .rule_flash_scene import check_flash_scene
from .rule_flash_speed import check_flash_speed
from .rule_flash_strobe import check_flash_strobe
from .rule_grid_order import check_grid_order
from .rule_group_grid import check_group_grids
from .rule_held_column import check_held_column
from .rule_intensity import check_intensity
from .rule_internal_program import check_internal_programs
from .rule_latched_strobe import check_latched_strobe
from .rule_masked_dimmer_efx import check_masked_dimmer_efx
from .rule_mode_owner import check_mode_owner
from .rule_movement_families import check_movement_families
from .rule_movement_window import check_movement_window
from .rule_pad_input import check_pad_input
from .rule_parked_movers import check_parked_movers
from .rule_shadowed_intensity import check_shadowed_intensity
from .rule_shutter_endpoint import check_shutter_endpoint
from .rule_smoke import check_smoke
from .rule_smoke_light import check_smoke_light
from .rule_smoke_restore import check_smoke_restore
from .rule_state_proxy import check_state_proxy
from .rule_stepped_dimmer import check_stepped_dimmer
from .rule_strobe_coverage import check_strobe_coverage
from .rule_strobe_in_cycle import check_strobe_in_cycle
from .rule_strobe_rate import check_strobe_rate
from .rule_strobe_restore import check_strobe_restore
from .rule_tap_dial import check_tap_dial
from .rule_tempo_units import check_tempo_units
from .rule_unaimed_movement import check_unaimed_movement
from .rule_undeclared_heads import check_undeclared_heads
from .rule_unfinished_effect import check_unfinished_effects
from .rule_wheel_colour import check_wheel_colour
from .rule_wheel_rotation import check_wheel_rotation
from .rule_zoom_narrow import check_zoom_narrow
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
    findings += check_wheel_rotation(graph, groups)
    findings += check_internal_programs(graph, groups, entries, states)
    findings += check_mode_owner(graph, groups, entries)
    findings += check_collisions(graph, groups, entries)
    findings += check_colour_clocks(graph, groups, entries, states)
    findings += check_unfinished_effects(graph, groups, entries)
    findings += check_strobe_in_cycle(graph, groups, entries)
    findings += check_strobe_rate(graph, groups, entries)
    findings += check_latched_strobe(graph, groups, entries)
    findings += check_flash_scene(graph, root)
    findings += check_flash_strobe(graph, groups, root)
    findings += check_flash_speed(graph, groups, root)
    findings += check_strobe_coverage(graph, groups)
    findings += check_shadowed_intensity(graph, groups, entries)
    findings += check_shutter_endpoint(graph, groups)
    findings += check_stepped_dimmer(graph, groups)
    findings += check_zoom_narrow(graph, groups)
    findings += check_masked_dimmer_efx(graph, groups, entries)
    findings += check_accent_restore(graph, groups, root, states)
    findings += check_strobe_restore(graph, groups, root, states)
    findings += check_state_proxy(graph, states)
    findings += check_tap_dial(root)
    findings += check_tempo_units(graph)
    findings += check_movement_families(graph)
    findings += check_parked_movers(graph)
    findings += check_unaimed_movement(graph)
    findings += check_movement_window(graph)
    findings += check_smoke(graph, groups, entries)
    findings += check_smoke_light(graph, groups, entries)
    findings += check_smoke_restore(graph, groups, root, states)
    findings += check_held_column(graph, groups, root)
    findings += check_group_grids(graph, root)
    findings += check_grid_order(root)
    findings += check_undeclared_heads(graph, root)
    findings += check_console(graph, root, canvas or _canvas(root))
    findings += check_audio_triggers(graph, groups, root)
    findings += check_pad_input(root)
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
