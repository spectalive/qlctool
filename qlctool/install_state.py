"""Whether QLC+ has this repo file: an identical copy, an older one, or none."""

import filecmp
from pathlib import Path

from .install_item import MISSING, STALE, SYNCED, InstallItem


def install_state(source: Path, destination: Path) -> InstallItem:
    if not destination.exists():
        state = MISSING
    elif filecmp.cmp(source, destination, shallow=False):
        state = SYNCED
    else:
        state = STALE
    return InstallItem(source, destination, state)
