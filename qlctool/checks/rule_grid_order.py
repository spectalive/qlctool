"""A fixture group whose cells are not in the order the fixtures stand in.

A matrix paints the grid a group declares, and half of QLC+'s scripts mean a
direction: Fill, Stripes, Random Column, Fill From Center all walk the cells
from one end to the other. That only reads as a sweep if cell 0 is at one side
of the room and the last cell at the other.

Nothing enforced it. A group is built in patch order - which is DMX address
order, which is cabling order - so `Cabezas` walked 9000, 10200, 1800, 3000,
4200, 5400, 6600, 7800, 1916, 9694, 4405, 7205 millimetres across the stage
(2026-08-31). Every sweep over the moving heads started house-right, jumped to
house-left, walked back, and jumped twice more. It is not a bug anybody can see
in the XML and it is not one the 3D view shows either: each fixture is drawn
where it stands, so only the *animation* is wrong, and only if you know what it
was supposed to look like.

The positions come from the `<Monitor>` node the plot writes, in millimetres, so
a workspace that has never been placed is excused - there are no sides to be out
of order. Fixtures sharing one position are excused against each other: an LED
bar is eight segments at one X, and their order is the bar's, not the stage's.

A fixture the plot marks as **not rigged** is checked too, and has to sit after
every rigged one. Its cell is not neutral: the matrix still paints it and nothing
lights, so a spare in the middle of a row is a hole in the middle of every sweep.
Leaving it out of the rule would also let the check pass on a group `--group-sort`
would still rewrite, which is a checker disagreeing with its own fixer.

`qlctool patch --group-sort GROUP` is the fix.
"""

import itertools

from lxml import etree

from ..fixture_groups import fixture_groups
from ..stage_x_positions import stage_x_positions
from .finding import WARNING, Finding
from .group_rows import group_rows
from .joined import Joined
from .row_jump import row_jump

RULE_ID = "grid_order"


def check_grid_order(root: etree._Element) -> list[Finding]:
    positions = stage_x_positions(root)
    if not positions:
        return []
    findings: list[Finding] = []
    for group in fixture_groups(root):
        for y, row in sorted(group_rows(root, group.group_id).items()):
            # An unplaced fixture sorts after every placed one, which is what
            # `--group-sort` does with it, so the same key answers both
            # questions: is the row in stage order, and are the spares last.
            keys = [
                (fixture_id not in positions, positions.get(fixture_id, 0.0))
                for _, fixture_id in sorted(row)
            ]
            out = [(before, after) for before, after in itertools.pairwise(keys) if after < before]
            if not out:
                continue
            findings.append(
                Finding(
                    rule_id=RULE_ID,
                    severity=WARNING,
                    function=group.name,
                    message_id="grid_order_row_jumps",
                    fields={
                        "row": y,
                        "count": len(out),
                        "jumps": Joined(tuple(row_jump(a, b) for a, b in out[:3]), ", "),
                        "more": ", ..." if len(out) > 3 else "",
                        "group": group.group_id,
                    },
                )
            )
    return findings
