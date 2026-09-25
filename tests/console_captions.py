"""Every caption a built show writes, for tests that ask what the console says."""

from pathlib import Path

from qlctool.workspace import Workspace


def console_captions(show: Path) -> list[str]:
    """The `Caption` of every element that carries one, in document order."""
    root = Workspace.load(show).root
    return [
        e.get("Caption") or "" for e in root.iter() if isinstance(e.tag, str) and e.get("Caption")
    ]
