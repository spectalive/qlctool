"""Copy the files of an install plan that QLC+ does not have yet."""

import shutil

from .install_item import InstallItem


def apply_install(items: list[InstallItem]) -> list[InstallItem]:
    """Copy every item that is missing or stale; return the ones copied."""
    copied: list[InstallItem] = []
    for item in items:
        if not item.needs_copy:
            continue
        item.destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(item.source, item.destination)
        copied.append(item)
    return copied
