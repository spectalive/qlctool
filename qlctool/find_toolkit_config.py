"""The `qlctool.toml` that governs a path: the nearest one at or above it."""

from pathlib import Path


def find_toolkit_config(start: Path) -> Path | None:
    """Walk up from `start` (a file or a folder) to the filesystem root."""
    here = start.resolve()
    for folder in (here, *here.parents):
        candidate = folder / "qlctool.toml"
        if candidate.is_file():
            return candidate
    return None
