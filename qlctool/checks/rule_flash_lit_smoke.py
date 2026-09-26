"""A held flash of the whole rig lights the lit smoke machines too.

The vertical fog machines carry LEDs, and with DMX connected those LEDs show
only what some function writes (`smoke_light`). `Flash 100%` has always
written them white; `Flash Color` - the strobe over whatever colour runs -
skipped every smoke fixture, so while it was held the four columns kept the
colour beneath, unstrobed, and read as dark next to the flash. The owner's
decision, 2026-09-26: "Si, el flash enciende las maquinas de humo en blanco".

The rule reads the wiring and the capabilities, never a name: a scene on a
`Flash`-action button that raises light (`flash_lights`) on every non-smoke
fixture with a dimmer or a strobe channel is a flash of the whole rig. Each lit
smoke machine (`is_lit_smoke`) it does not light is a column sitting the flash
out. The smoke burst, a colour bank, a gobo pick and `Strobo Rapido` raise
light on no fixture or only on some, and are left alone.
"""

from lxml import etree

from .. import roles
from ..vc.button import NO_FUNCTION
from ..xmlutil import find_local, iter_local
from .finding import ERROR, Finding
from .flash_lights import flash_lights
from .show_graph import ShowGraph
from .strobe_written import strobe_capable_offsets

RULE_ID = "flash_lit_smoke"


def check_flash_lit_smoke(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], root: etree._Element
) -> list[Finding]:
    console = find_local(root, "VirtualConsole")
    if console is None:
        return []
    columns = [c for c in graph.capabilities.values() if c.is_lit_smoke]
    reachable = [
        c
        for c in graph.capabilities.values()
        if not c.is_smoke and (c.offsets_for_role(roles.DIMMER) or strobe_capable_offsets(c))
    ]
    if not columns or not reachable:
        return []
    findings: list[Finding] = []
    seen: set[int] = set()
    for button in iter_local(console, "Button"):
        action = find_local(button, "Action")
        function = find_local(button, "Function")
        if action is None or (action.text or "").strip() != "Flash" or function is None:
            continue
        function_id = int(function.attrib.get("ID", NO_FUNCTION))
        if function_id == NO_FUNCTION or function_id in seen:
            continue
        seen.add(function_id)
        scene = graph.functions.get(function_id)
        if scene is None or scene.attrib.get("Type") != "Scene":
            continue  # rule_flash_scene already reports that wiring
        written = graph.driven_of(scene, groups)
        lights = {
            c.fixture.fixture_id
            for c in [*reachable, *columns]
            if flash_lights(c, written.get(c.fixture.fixture_id, {}))
        }
        if not all(c.fixture.fixture_id in lights for c in reachable):
            continue
        dark = sorted(c.fixture.name for c in columns if c.fixture.fixture_id not in lights)
        if dark:
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=ERROR,
                    function=graph.name(function_id),
                    fixtures=tuple(dark),
                    message_id="flash_lit_smoke_column_dark",
                    fields={"count": len(dark)},
                )
            )
    return findings
