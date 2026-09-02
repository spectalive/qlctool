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
wheels there (`exclude_fade`); a hand-patched fixture or a definition that
grew a wheel is what this catches.
"""

from lxml import etree

from ..excluded_fades import excluded_fades
from ..wheel_fade_offsets import wheel_fade_offsets
from ..xmlutil import find_local, findall_local
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "rueda fundida"


def check_wheel_fade(graph: ShowGraph, groups, root: etree._Element) -> list[Finding]:
    excluded = excluded_fades(root)
    wheels = {
        fixture_id: set(wheel_fade_offsets(capability))
        for fixture_id, capability in graph.capabilities.items()
    }
    fades = _fade_of_every_scene(graph)
    findings: list[Finding] = []
    for scene_id, fade in sorted(fades.items()):
        if fade <= 0:
            continue
        scene = graph.functions[scene_id]
        crossed: list[str] = []
        for fixture_id, written in driven_channels(scene, graph.capabilities, groups).items():
            hit = (set(written) & wheels.get(fixture_id, set())) - excluded.get(fixture_id, set())
            if hit:
                name = graph.capabilities[fixture_id].fixture.name
                crossed.extend(f"{name} ch{offset + 1}" for offset in sorted(hit))
        if not crossed:
            continue
        findings.append(
            Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(scene_id),
                fixtures=tuple(crossed),
                message=(
                    f"se funde en {fade} ms y escribe una rueda que su fixture no "
                    f"excluye del fundido (<ExcludeFade>): la rueda mecanica "
                    f"recorre todos los colores o gobos intermedios en cada paso"
                ),
            )
        )
    return findings


def _fade_of_every_scene(graph: ShowGraph) -> dict[int, int]:
    """Scene id -> the longest fade-in it is started with, its own included."""
    fades: dict[int, int] = {}
    for function_id, function in graph.functions.items():
        kind = function.attrib.get("Type")
        if kind == "Scene":
            fades[function_id] = max(fades.get(function_id, 0), _own_fade(function))
        elif kind == "Chaser":
            common = _own_fade(function)
            per_step = _speed_mode(function) == "PerStep"
            for step in findall_local(function, "Step"):
                if not (step.text and step.text.strip().isdigit()):
                    continue
                target = int(step.text)
                fade = int(step.attrib.get("FadeIn", "0")) if per_step else common
                # A Collection in between changes nothing: `Collection::write`
                # hands the chaser's override fade to every member.
                for scene_id in _scenes_under(graph, target):
                    fades[scene_id] = max(fades.get(scene_id, 0), fade)
    return fades


def _scenes_under(graph: ShowGraph, function_id: int) -> list[int]:
    kind = graph.kind(function_id)
    if kind == "Scene":
        return [function_id]
    if kind != "Collection":
        return []
    found: list[int] = []
    for member in graph.members.get(function_id, ()):
        found += _scenes_under(graph, member)
    return found


def _own_fade(function: etree._Element) -> int:
    speed = find_local(function, "Speed")
    return int(speed.attrib.get("FadeIn", "0")) if speed is not None else 0


def _speed_mode(function: etree._Element) -> str:
    modes = find_local(function, "SpeedModes")
    return modes.attrib.get("FadeIn", "Common") if modes is not None else "Common"
