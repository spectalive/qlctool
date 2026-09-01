"""A fixture group whose grid does not match the lights in it.

An RGBMatrix paints the cells a group **declares**, and two things go wrong
when the declaration and the heads disagree.

A cell with **no head** is a frame of every sweep where that part of the group
is simply dark. It is not subtle: `BarrasLed` was 8x3 with four empty cells in
its bottom row, and the four wall panels beside them sat unlit through the
first half of every Fill - "la mitad de la barra led los pixeles leds estan
apagados" (owner, 2026-08-26).

A head **outside** the grid is a fixture no effect can ever reach. `Cabezas`
declared 8x1 over twelve heads, so four of them were invisible to every matrix
in the show.

The rule is one sentence: a group's grid is exactly as big as the group. The
way out is usually not a bigger grid - it is noticing that two kinds of light
were sharing one picture, and giving them a group each.
"""

from lxml import etree

from ..xmlutil import find_local, findall_local, iter_local
from .finding import ERROR, Finding
from .show_graph import ShowGraph

RULE = "rejilla"


def check_group_grids(graph: ShowGraph, root: etree._Element) -> list[Finding]:
    del graph
    findings: list[Finding] = []
    for group in iter_local(root, "FixtureGroup"):
        if "ID" not in group.attrib:
            continue  # a plain <FixtureGroup>0</FixtureGroup> reference
        size = find_local(group, "Size")
        if size is None:
            continue
        width, height = int(size.attrib["X"]), int(size.attrib["Y"])
        cells = [
            (int(head.attrib["X"]), int(head.attrib["Y"])) for head in findall_local(group, "Head")
        ]
        name = _name(group)

        outside = [cell for cell in cells if cell[0] >= width or cell[1] >= height]
        if outside:
            findings.append(
                Finding(
                    rule=RULE,
                    severity=ERROR,
                    function=name,
                    message=(
                        f"declara {width}x{height} pero tiene {len(outside)} head(s) "
                        f"fuera de esa rejilla: ningun efecto los alcanza"
                    ),
                )
            )

        empty = width * height - len({c for c in cells if c not in outside})
        if empty > 0:
            findings.append(
                Finding(
                    rule=RULE,
                    severity=ERROR,
                    function=name,
                    message=(
                        f"declara {width}x{height} = {width * height} celdas y solo "
                        f"{width * height - empty} tienen luz: en cada barrido "
                        f"{empty} celda(s) se quedan a oscuras sin motivo"
                    ),
                )
            )
    return findings


def _name(group: etree._Element) -> str:
    name = find_local(group, "Name")
    return (name.text or "").strip() if name is not None else group.attrib["ID"]
