"""Every pair of patched fixtures in a workspace whose channel ranges overlap."""

from lxml import etree

from .patch_conflict import PatchConflict
from .patched_fixtures import patched_fixtures


def patch_conflicts(root: etree._Element) -> list[PatchConflict]:
    """Every pair of patched fixtures whose channel ranges overlap."""
    fixtures = sorted(patched_fixtures(root), key=lambda f: (f.universe, f.address))
    conflicts = []
    for index, first in enumerate(fixtures):
        for second in fixtures[index + 1 :]:
            if second.universe != first.universe:
                continue
            if second.address >= first.address + first.channels:
                break  # sorted by address: nothing further can overlap
            start = max(first.address, second.address)
            stop = min(first.address + first.channels, second.address + second.channels)
            conflicts.append(
                PatchConflict(
                    first=first,
                    second=second,
                    universe=first.universe,
                    overlap=range(start, stop),
                )
            )
    return conflicts
