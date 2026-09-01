"""Move a patched fixture to another DMX address or universe.

Re-addressing is the operation with the worst failure mode - two fixtures on the
same channels look fine in the file and wrong on stage - so the move is applied,
then the whole patch is re-checked, and it is rolled back if it collides.
"""

from lxml import etree

from ..patch_conflicts import PatchConflict, patch_conflicts
from ..xmlutil import find_local
from .patch_element import patch_element


def set_fixture_address(
    root: etree._Element,
    fixture_id: int,
    address: int,
    universe: int | None = None,
    allow_overlap: bool = False,
) -> list[PatchConflict]:
    """Re-address one fixture; returns the conflicts the move introduced.

    address is 0-based, as the file stores it - QLC+'s UI shows it 1-based. A
    move that collides with another fixture is undone and raises, unless
    allow_overlap says the caller means it (returning the conflicts instead).
    """
    element = patch_element(root, fixture_id)
    address_element = find_local(element, "Address")
    universe_element = find_local(element, "Universe")

    previous_address = address_element.text
    previous_universe = universe_element.text

    address_element.text = str(address)
    if universe is not None:
        universe_element.text = str(universe)

    introduced = [
        conflict
        for conflict in patch_conflicts(root)
        if fixture_id in (conflict.first.fixture_id, conflict.second.fixture_id)
    ]
    if introduced and not allow_overlap:
        address_element.text = previous_address
        universe_element.text = previous_universe
        raise ValueError(
            "re-address would overlap: " + "; ".join(conflict.describe() for conflict in introduced)
        )
    return introduced
