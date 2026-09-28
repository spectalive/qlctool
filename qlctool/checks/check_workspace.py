"""Run every check over a workspace and return what is wrong with the show.

This is the answer to a show that worked by luck. QLC+'s own validation says
the file loads; these say the room will do what the buttons promise - that
nothing lit is dark, that no two programmes are writing the same colour, that
the fixtures without RGB were not silently skipped, and that the console cannot
be pressed into a state the show was never built for.

Every rule here exists because something went wrong in a real room; adding one
is how a bug stops being able to happen twice. A controller's rules come from the
`qlctool.rules` entry points (`checks/rule_providers.py`), each only where its controller is.
"""

from collections.abc import Sequence

from ..capabilities_of import capabilities_of
from ..fixture_library import FixtureLibrary
from ..names.names import Names
from ..workspace import Workspace
from .applying_providers import applying_providers
from .build_show_graph import build_show_graph
from .console_findings import console_findings
from .entry_points import entry_points
from .family_frame_findings import family_frame_findings
from .finding import Finding
from .fixing_order import fixing_order
from .flash_button_findings import flash_button_findings
from .group_fixtures import group_fixtures
from .movement_findings import movement_findings
from .named_findings import named_findings
from .room_states import room_states
from .rule_accent_restore import check_accent_restore
from .rule_collision import check_collisions
from .rule_colour_animation_wheel import check_colour_animation_wheel
from .rule_colour_clocks import check_colour_clocks
from .rule_context import RuleContext
from .rule_dangling_reference import check_dangling_references
from .rule_duplicate_fixture_id import check_duplicate_fixture_ids
from .rule_grid_order import check_grid_order
from .rule_group_grid import check_group_grids
from .rule_held_column import check_held_column
from .rule_instant_dimmer import check_instant_dimmer
from .rule_intensity import check_intensity
from .rule_internal_program import check_internal_programs
from .rule_invisible_matrix import check_invisible_matrix
from .rule_latched_strobe import check_latched_strobe
from .rule_layer_adds import check_layer_adds
from .rule_layer_trace import check_layer_trace
from .rule_masked_dimmer_efx import check_masked_dimmer_efx
from .rule_missing_definition import check_missing_definitions
from .rule_mode_owner import check_mode_owner
from .rule_movement_figure_coverage import check_movement_figure_coverage
from .rule_pick_overridden import check_pick_overridden
from .rule_provider import RuleProvider
from .rule_shadowed_intensity import check_shadowed_intensity
from .rule_shutter_endpoint import check_shutter_endpoint
from .rule_smoke import check_smoke
from .rule_smoke_light import check_smoke_light
from .rule_smoke_restore import check_smoke_restore
from .rule_solo_handoff import check_solo_handoff
from .rule_split_complementary import check_split_complementary
from .rule_state_handover import check_state_handover
from .rule_state_palette import check_state_palette
from .rule_state_proxy import check_state_proxy
from .rule_stepped_dimmer import check_stepped_dimmer
from .rule_strobe_black import check_strobe_black
from .rule_strobe_coverage import check_strobe_coverage
from .rule_strobe_in_cycle import check_strobe_in_cycle
from .rule_strobe_rate import check_strobe_rate
from .rule_strobe_restore import check_strobe_restore
from .rule_tap_dial import check_tap_dial
from .rule_tempo_units import check_tempo_units
from .rule_undeclared_heads import check_undeclared_heads
from .rule_unfinished_effect import check_unfinished_effects
from .rule_unreachable_function import check_unreachable_functions
from .rule_untempoed_rhythm import check_untempoed_rhythm
from .rule_wheel_colour import check_wheel_colour
from .rule_wheel_fade import check_wheel_fade
from .rule_wheel_rotation import check_wheel_rotation
from .rule_wheel_white import check_wheel_white
from .rule_white_emitter import check_white_emitter
from .rule_white_share_dropped import check_white_share_dropped
from .rule_white_twice import check_white_twice
from .rule_zoom_narrow import check_zoom_narrow


def check_workspace(
    workspace: Workspace,
    library: FixtureLibrary,
    canvas: tuple[int, int] | None = None,
    providers: Sequence[RuleProvider] | None = None,
    names: Names | None = None,
) -> list[Finding]:
    """Every finding, worst first, in the order a person would fix them.

    With `names` (a description's vocabulary) the findings are worded in it;
    without, in the language the workspace was generated in.
    """
    root = workspace.root
    capabilities = capabilities_of(root, library)
    graph = build_show_graph(root, capabilities)
    groups = group_fixtures(root)
    entries = entry_points(root)
    states = room_states(root, graph, groups)
    context = RuleContext(root=root, graph=graph, groups=groups, entries=entries, states=states)
    applying = applying_providers(root, providers)
    bounded = frozenset().union(*(p.bounded_latches(context) for p in applying))

    findings: list[Finding] = []
    findings += check_missing_definitions(root, library)
    findings += check_duplicate_fixture_ids(root)
    findings += check_dangling_references(graph, root)
    findings += check_unreachable_functions(root)
    findings += check_intensity(graph, groups, entries, states)
    findings += check_instant_dimmer(graph, groups, states)
    findings += check_white_emitter(graph, groups)
    findings += check_white_twice(graph, groups)
    findings += check_white_share_dropped(graph, groups)
    findings += check_wheel_colour(graph, groups, entries)
    findings += check_colour_animation_wheel(graph, groups, entries)
    findings += check_movement_figure_coverage(graph, groups, entries, root)
    findings += check_wheel_rotation(graph, groups)
    findings += check_wheel_fade(graph, groups, root)
    findings += check_internal_programs(graph, groups, entries, states)
    findings += check_mode_owner(graph, groups, entries)
    findings += check_collisions(graph, groups, entries, states)
    findings += check_layer_adds(graph, groups, root, states)
    findings += check_layer_trace(graph, groups, root, states)
    findings += check_pick_overridden(graph, groups, root, states)
    findings += family_frame_findings(graph, groups, root, states)
    findings += check_solo_handoff(graph, root, states)
    findings += check_state_handover(graph, groups, states)
    findings += check_colour_clocks(graph, groups, entries, states)
    findings += check_wheel_white(graph, groups, entries)
    findings += check_state_palette(graph, groups, entries, states)
    findings += check_split_complementary(graph, groups, entries)
    findings += check_unfinished_effects(graph, groups, entries)
    findings += check_strobe_in_cycle(graph, groups, entries)
    findings += check_strobe_rate(graph, groups, entries)
    findings += check_latched_strobe(graph, groups, entries)
    findings += check_strobe_black(graph, groups, root, states)
    findings += flash_button_findings(graph, groups, root, states, entries)
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
    findings += check_untempoed_rhythm(graph, groups, root, entries)
    findings += check_tempo_units(graph)
    findings += movement_findings(graph, groups, root, states)
    findings += check_smoke(graph, groups)
    findings += check_smoke_light(graph, groups)
    findings += check_smoke_restore(graph, groups, root)
    findings += check_held_column(graph, groups, root, bounded)
    findings += check_group_grids(graph, root)
    findings += check_grid_order(root)
    findings += check_invisible_matrix(graph, root)
    findings += check_undeclared_heads(graph, root)
    findings += console_findings(graph, groups, root, states, canvas)
    findings += [finding for provider in applying for finding in provider.check(context)]
    return fixing_order(named_findings(findings, root, names))
