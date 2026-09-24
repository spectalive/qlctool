"""Which folders hold a rig's fixture definitions (ruling B3).

The first source that names any folder wins: the command line, then the
description's [rig] fixtures, then QLCTOOL_FIXTURES, then the nearest
qlctool.toml found walking up from the workspace or the description, then
from the current directory.
"""

import os
from collections.abc import Mapping, Sequence
from pathlib import Path

from .toolkit_config_from import toolkit_config_from


def fixture_dirs(
    cli: Sequence[str] = (),
    described: Sequence[Path] = (),
    environ: Mapping[str, str] | None = None,
    start: Path | None = None,
) -> tuple[Path, ...]:
    """Folders in priority order: the first one wins a model clash."""
    if cli:
        return tuple(Path(entry) for entry in cli)
    if described:
        return tuple(described)
    variable = (os.environ if environ is None else environ).get("QLCTOOL_FIXTURES", "")
    listed = [entry for entry in variable.split(os.pathsep) if entry]
    if listed:
        return tuple(Path(entry) for entry in listed)
    return toolkit_config_from(Path.cwd() if start is None else start).fixtures
