"""One <FixtureGroup> grid a workspace defines.

An RGBMatrix paints onto a fixture group's X/Y grid, so generating matrix
effects "for the LED bars" needs the group's ID and name. This reads only the
group definitions; the same local name also appears inside RGBMatrix functions
as a plain ID reference, and those are filtered out.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DefinedFixtureGroup:
    group_id: int
    name: str
    width: int
    height: int
    head_count: int
    fixture_ids: tuple[int, ...]  # in grid order, each fixture once
