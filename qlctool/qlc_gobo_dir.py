"""Where QLC+ resolves a definition's relative gobo images.

There is no user-level gobo folder: `QLCCapability::loadXML` resolves a
relative `Res1` against the application's own Gobos directory, so the images
have to go inside the bundle and go again after every QLC+ upgrade.
"""

from pathlib import Path

from .validate import qlcplus_binary


def qlc_gobo_dir(binary: str | None = None) -> Path | None:
    """The installed QLC+'s Gobos folder, or None when no QLC+ is installed."""
    executable = binary or qlcplus_binary()
    if executable is None:
        return None
    for parent in Path(executable).parents:
        if parent.suffix == ".app":
            return parent / "Contents" / "Resources" / "Gobos"
        if parent.name in ("bin", "MacOS"):
            candidate = parent.parent / "share" / "qlcplus" / "gobos"
            if candidate.is_dir():
                return candidate
    return None
