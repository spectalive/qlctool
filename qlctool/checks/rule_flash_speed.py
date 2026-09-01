"""A flash that strobes, but at a stroll.

2026-08-29, the owner watching the PARs: "el flash para las par leds es entre
246-248 (strobo), como lo tenemos ahora es muy lento". The generator sat every
fast flash at 0.85 of the slow-to-fast run - 217 on the CLB2.4's 1-255 strobe
channel - while the hand-built show it replaced drove the rig near the top of
each channel (CromoWash 240 of 10-255, Vortex 250 of 255, panels 255). The
only rule watching the flash asked whether it strobes at all, never whether it
strobes like a flash, so a whole rig flashing at a stroll passed every check.

The rule: on every strobe channel the hand-pressed Flash buttons drive, the
*fastest* value any of them writes must sit near the top of that channel's
slow-to-fast run. A slower flash beside it is fine - half speed is a choice
the hand-built console also made - but the console's fastest flash has to
actually be fast. Speed is read off capabilities, never off a name: a labelled
strobing range measures from its slow end, a bare speed channel from zero, and
a `StrobeFastToSlow` range runs backwards.

And the slower flash has a floor of its own. Same night, same owner: "el flash
slow para los par es unos 200" - 0.78 of the CLB2.4's run - while the
generator's 0.45 had it at 115, a crawl no one would call a flash. So: every
strobing value a hand-pressed Flash button writes sits above the crawl line,
fast or slow.
"""

from lxml import etree

from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, iter_local
from .audio_pressed_widgets import audio_pressed_widgets
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph
from .strobe_written import strobe_capable_offsets, value_strobes

RULE = "flash lento"

# Where "fast" starts on the slow-to-fast run. The slowest fast flash the
# hand-built show ever used was the CromoWash's 240 of 10-255 (0.94); the
# owner's 246-248 on the CLB2.4 is 0.965-0.973; the 0.85 that shipped is well
# below either.
FAST_FLASH_FRACTION = 0.93

# Below this, a "flash" is a crawl. The owner's slow flash is ~200 of the
# CLB2.4's 1-255 (0.78); the 0.45 that shipped (115) is well under, and the
# floor sits between them with margin to both.
CRAWL_FLASH_FRACTION = 0.7

FAST_TO_SLOW_PRESET = "StrobeFastToSlow"


def check_flash_speed(graph: ShowGraph, groups, root: etree._Element) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    # (fixture, offset) -> the fastest fraction any flash reaches, and whose.
    best: dict[tuple[int, int], tuple[float, str]] = {}
    # scene -> the writes that sit below the crawl line, fast flash or not.
    crawl_by_scene: dict[str, list[tuple[int, float]]] = {}
    for function_id in _hand_flash_scenes(graph, console):
        scene = graph.functions[function_id]
        for fixture_id, written in driven_channels(scene, graph.capabilities, groups).items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None or capability.is_smoke:
                continue
            for offset, strobing in strobe_capable_offsets(capability).items():
                value = written.get(offset)
                if value is None or not value_strobes(strobing, value):
                    continue
                fraction = _speed_fraction(strobing, value)
                key = (fixture_id, offset)
                if key not in best or fraction > best[key][0]:
                    best[key] = (fraction, graph.name(function_id))
                if fraction < CRAWL_FLASH_FRACTION:
                    crawl_by_scene.setdefault(graph.name(function_id), []).append(
                        (fixture_id, fraction)
                    )
    slow_by_scene: dict[str, list[tuple[int, float]]] = {}
    for (fixture_id, offset), (fraction, scene_name) in sorted(best.items()):
        if fraction < FAST_FLASH_FRACTION:
            slow_by_scene.setdefault(scene_name, []).append((fixture_id, fraction))
    findings: list[Finding] = []
    for scene_name, slow in sorted(slow_by_scene.items()):
        names = sorted(
            {
                graph.capabilities[fixture_id].fixture.name or str(fixture_id)
                for fixture_id, _ in slow
            }
        )
        slowest = min(fraction for _, fraction in slow)
        findings.append(
            Finding(
                rule=RULE,
                severity=ERROR,
                function=scene_name,
                fixtures=tuple(names),
                message=(
                    f"es el flash mas rapido que reciben {len(slow)} canales de "
                    f"estrobo y se queda al {slowest:.0%} de su carrera "
                    f"slow-to-fast - un flash a toda velocidad vive del "
                    f"{FAST_FLASH_FRACTION:.0%} para arriba"
                ),
            )
        )
    for scene_name, crawling in sorted(crawl_by_scene.items()):
        names = sorted(
            {
                graph.capabilities[fixture_id].fixture.name or str(fixture_id)
                for fixture_id, _ in crawling
            }
        )
        slowest = min(fraction for _, fraction in crawling)
        findings.append(
            Finding(
                rule=RULE,
                severity=ERROR,
                function=scene_name,
                fixtures=tuple(names),
                message=(
                    f"escribe {len(crawling)} canales de estrobo por debajo del "
                    f"{CRAWL_FLASH_FRACTION:.0%} de su carrera slow-to-fast (el "
                    f"peor al {slowest:.0%}) - eso ya no es un flash, es un "
                    f"parpadeo a paso de tortuga"
                ),
            )
        )
    return findings


def _hand_flash_scenes(graph: ShowGraph, console: etree._Element):
    """Scenes behind Flash buttons a finger presses, not an audio bar."""
    audio_pressed = audio_pressed_widgets(console)
    seen: set[int] = set()
    for button in iter_local(console, "Button"):
        action = find_local(button, "Action")
        if action is None or (action.text or "").strip() != "Flash":
            continue
        if button.attrib.get("ID", "") in audio_pressed:
            continue
        function = find_local(button, "Function")
        if function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id == NO_FUNCTION or function_id in seen:
            continue
        scene = graph.functions.get(function_id)
        if scene is None or scene.attrib.get("Type") != "Scene":
            continue  # rule_flash_scene already reports that wiring
        seen.add(function_id)
        yield function_id


def _speed_fraction(strobing, value: int) -> float:
    """Where a strobing value sits on its channel's slow-to-fast run."""
    if strobing is None:
        return value / 255
    span = strobing.maximum - strobing.minimum
    if span == 0:
        return 1.0
    fraction = (value - strobing.minimum) / span
    if strobing.preset == FAST_TO_SLOW_PRESET:
        return 1.0 - fraction
    return fraction
