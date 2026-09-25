"""Two opposite colours mixed inside one wash.

HARMAN's rule for concert colour, in the design note the show is built on
(`brain/topics/stage-lighting-design`): complementary colours **on the same
surface desaturate each other towards white**, so the contrast belongs
*between* roles - the heads against the PARs - and never inside one wash.
The mix wheels broke it thirty times a night: "Azul / Amarillo PAR" is the
PARs on a truss alternating blue and yellow, and where their pools overlap
on the floor the room gets the one colour the owner asked to keep out of
every rotation (2026-09-22, "cuales casan mejor o usan los prods").

The shape: a Scene, reachable from a button, that puts **exactly two** lit,
saturated colours on the members of one fixture group, with the two hues 150
degrees or more apart. Exactly two, because that is what a split is; a deal
of four or of seventeen is the multicolour look, wild on purpose and on a
button of its own. Saturated, because a pastel has too little hue to fight.
The rule reasons about the values and the groups, never about a name.
"""

from ..complementary_from import COMPLEMENTARY_FROM
from ..hue_distance import hue_distance
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .fixture_colour import fixture_colour
from .saturated import saturated
from .show_graph import ShowGraph

RULE = "complementarios en un mismo lavado"
STATES_COLOUR = ("Scene", "Sequence")


def check_split_complementary(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], entries: dict[int, str]
) -> list[Finding]:
    findings: list[Finding] = []
    judged: dict[int, str] = {}
    for function_id, caption in sorted(entries.items()):
        for member in sorted(graph.descendants(function_id)):
            if graph.kind(member) in STATES_COLOUR:
                judged.setdefault(member, caption)
    for scene_id, caption in sorted(judged.items()):
        written = driven_channels(graph.functions[scene_id], graph.capabilities, {})
        for _group_id, members in sorted(groups.items()):
            colours = {
                colour
                for fixture_id in members
                if fixture_id in written
                and (colour := fixture_colour(graph, fixture_id, written[fixture_id])) is not None
                and any(colour)
                and saturated(colour)
            }
            if len(colours) != 2:
                continue
            first, second = sorted(colours)
            apart = hue_distance(first, second)
            if apart < COMPLEMENTARY_FROM:
                continue
            findings.append(
                Finding(
                    rule=RULE,
                    severity=ERROR,
                    function=graph.name(scene_id),
                    fixtures=tuple(
                        sorted(
                            graph.capabilities[fixture_id].fixture.name
                            for fixture_id in members
                            if fixture_id in graph.capabilities and fixture_id in written
                        )
                    ),
                    message=(
                        f"alterna dos colores opuestos ({apart:.0f} grados) dentro de un "
                        "mismo grupo: donde se solapan se desaturan hacia blanco. Los "
                        "complementarios van entre roles (cabezas contra resto); en un "
                        f"mismo lavado, colores vecinos (boton: {caption})"
                    ),
                )
            )
    return findings
