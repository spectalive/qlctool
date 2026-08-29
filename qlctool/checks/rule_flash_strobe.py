"""A flash that lights the room without strobing it.

In this show a held flash *is* the strobe: the hand-built console's
`Flash 100%` drove every shutter on the rig near the top of its range, and its
`Flash 50%` was the same white at half the speed. The generated show quietly
replaced that with a steady work light - full white, shutters parked "Open" -
and the owner caught it at home on 2026-08-27: "esto no hace estrobo y antes
lo hacia cuando le daba al espacio".

The rule reads the wiring, not the name: every scene a `Flash`-action button
drives must, on each fixture it writes that has a strobe-capable channel, put
that channel into a value that actually strobes (`strobe_written`). A fixture
the scene leaves out entirely is somebody else's business - the smoke burst is
also a Flash button and touches nothing with a shutter - but writing a fixture
while parking its shutter in "Open" or "No function" is exactly the shape of
the regression.

One structural exception, cutting both ways: a Flash button that an
AudioTriggers bar presses is worked by the PA, not by a finger, and a strobe
fired by whatever the music does is a strobe nobody chose. That button is
*required* not to strobe - the same wiring that exempts it from the first
half of the rule binds it to the second.
"""

from lxml import etree

from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, iter_local
from .audio_pressed_widgets import audio_pressed_widgets
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph
from .strobe_written import strobe_capable_offsets, value_strobes

RULE = "flash sin estrobo"
AUDIO_RULE = "estrobo en manos del audio"


def check_flash_strobe(
    graph: ShowGraph, groups, root: etree._Element
) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    audio_pressed = audio_pressed_widgets(console)
    findings: list[Finding] = []
    seen: set[int] = set()
    for button in iter_local(console, "Button"):
        action = find_local(button, "Action")
        if action is None or (action.text or "").strip() != "Flash":
            continue
        function = find_local(button, "Function")
        if function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id == NO_FUNCTION or function_id in seen:
            continue
        seen.add(function_id)
        scene = graph.functions.get(function_id)
        if scene is None or scene.attrib.get("Type") != "Scene":
            continue  # rule_flash_scene already reports that wiring
        by_audio = button.attrib.get("ID", "") in audio_pressed
        dark, strobing = _strobe_writes(graph, groups, scene)
        if by_audio and strobing:
            findings.append(Finding(
                rule=AUDIO_RULE,
                severity=ERROR,
                function=graph.name(function_id),
                message=(
                    f"estroba y lo pulsa una barra de audio: un estrobo "
                    f"disparado por lo que haga la musica es un estrobo que "
                    f"nadie ha elegido"
                ),
            ))
        elif not by_audio and dark:
            findings.append(Finding(
                rule=RULE,
                severity=ERROR,
                function=graph.name(function_id),
                fixtures=tuple(sorted(dark)),
                message=(
                    f"cuelga de un boton Flash y escribe {len(dark)} aparatos "
                    f"con canal de estrobo sin estrobarlos - en este show un "
                    f"flash mantenido estroba, y dejar el shutter en "
                    f"«Open»/«No function» es la luz de trabajo, no el golpe"
                ),
            ))
    return findings


def _strobe_writes(graph: ShowGraph, groups, scene) -> tuple[list[str], bool]:
    """(fixtures written but not strobed, whether anything strobes at all)."""
    dark: list[str] = []
    strobing_anywhere = False
    for fixture_id, written in driven_channels(
        scene, graph.capabilities, groups
    ).items():
        capability = graph.capabilities.get(fixture_id)
        if capability is None or capability.is_smoke:
            continue
        capable = strobe_capable_offsets(capability)
        if not capable:
            continue
        strobed = any(
            offset in written
            and written[offset] is not None
            and value_strobes(strobing, written[offset])
            for offset, strobing in capable.items()
        )
        if strobed:
            strobing_anywhere = True
        else:
            dark.append(capability.fixture.name or str(fixture_id))
    return dark, strobing_anywhere
