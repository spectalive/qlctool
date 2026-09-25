"""A step, a button or a timeline that names a function the show does not have.

2026-09-25, Plan C preflight: the first show built for a rig with no gobo
wheel wrote `Talk Light` as a Collection of the talk scene and the beams'
white - and there were no beams' white, so the second step read
`<Step Number="1">None</Step>`. QLC+ loaded it without a word and every rule
passed it, because the function graph only follows steps that are numbers.
The generator had asked for a member that was never built, and the file said
so in plain text.

The rule is the graph's own question asked of every reference instead of only
the well-formed ones: whatever a Collection or Chaser step, a Show track, a
Sequence or a console widget names must be the id of a function in this
workspace. A step that is not a number, or a number nobody carries, starts
nothing - and a button that starts nothing is a promise the room cannot keep.
"""

from lxml import etree

from .finding import ERROR, Finding
from .function_references import function_references
from .show_graph import ShowGraph

RULE_ID = "dangling_reference"


def check_dangling_references(graph: ShowGraph, root: etree._Element) -> list[Finding]:
    findings: list[Finding] = []
    for holder, raw in function_references(root):
        if raw.isdigit() and int(raw) in graph.functions:
            continue
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=ERROR,
                function=holder,
                message=(
                    f"nombra la funcion {raw or '(vacio)'}, que no existe en este "
                    f"workspace: ese paso o ese boton no arranca nada"
                ),
            )
        )
    return findings
