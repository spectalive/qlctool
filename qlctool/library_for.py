"""The fixture library a command works with, found from where its files are."""

from collections.abc import Sequence
from pathlib import Path

from .fixture_dirs import fixture_dirs
from .library import FixtureLibrary


def library_for(
    cli: Sequence[str] | None, start: Path, described: Sequence[Path] = ()
) -> FixtureLibrary:
    """`--fixtures`, the description, QLCTOOL_FIXTURES, then qlctool.toml from `start`.

    When nothing names a folder from `start`, the nearest qlctool.toml above the
    current directory still counts (ruling B3: "or the current directory").
    """
    folders = fixture_dirs(cli or (), described, None, start) or fixture_dirs(
        (), (), None, Path.cwd()
    )
    return FixtureLibrary.load(folders)
