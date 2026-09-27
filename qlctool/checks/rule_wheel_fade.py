"""A fade that crosses a mechanical wheel between its detents.

QLC+ fades every channel a scene writes unless the fixture lists it in
`<ExcludeFade>` (`Fixture::channelCanFade`), and a FadeChannel starts from
the value the universe currently holds. So the rig-wide colour wheel's 800 ms
crossfade did not only soften the LEDs: on the four BEAM 230W 7R it walked the
colour wheel from Red (12) to Blue (43) through orange, yellow and green,
twenty-one steps every 3.3 seconds, all night, and the per-group wheels did
the same in 400 ms (cross-audit, 2026-09-02). A wheel is a set of detents; the
values between two of them are half of each, and `rueda de color girando`
only ever looked at where a step *ends*.

The rule reads the wiring: every scene that is a chaser step (or carries a
fade of its own) and writes a colour, gobo or prism wheel with a non-zero fade
must find that wheel in the fixture's `<ExcludeFade>`. The generator pins the
wheels there (`pin_wheel_fades`); a hand-patched fixture or a definition that
grew a wheel is what this catches.
"""

from lxml import etree

from ..excluded_fades import excluded_fades
from ..wheel_fade_offsets import wheel_fade_offsets
from .fade_of_every_scene import fade_of_every_scene
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE_ID = "wheel_fade"


def check_wheel_fade(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], root: etree._Element
) -> list[Finding]:
    excluded = excluded_fades(root)
    wheels = {
        fixture_id: set(wheel_fade_offsets(capability))
        for fixture_id, capability in graph.capabilities.items()
    }
    fades = fade_of_every_scene(graph)
    findings: list[Finding] = []
    for scene_id, fade in sorted(fades.items()):
        if fade <= 0:
            continue
        scene = graph.functions[scene_id]
        crossed: list[str] = []
        for fixture_id, written in graph.driven_of(scene, groups).items():
            hit = (set(written) & wheels.get(fixture_id, set())) - excluded.get(fixture_id, set())
            if hit:
                name = graph.capabilities[fixture_id].fixture.name
                crossed.extend(f"{name} ch{offset + 1}" for offset in sorted(hit))
        if not crossed:
            continue
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=ERROR,
                function=graph.name(scene_id),
                fixtures=tuple(crossed),
                message_id="wheel_fade_crossed",
                fields={"fade": fade},
            )
        )
    return findings
