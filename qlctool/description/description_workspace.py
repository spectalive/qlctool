"""The workspace a description's [rig] names, needed before the rest can be validated."""

from pathlib import Path

from .reading.read_rig import read_rig
from .reading.read_toml_file import read_toml_file
from .reading.table_at import table_at


def description_workspace(path: str | Path) -> Path:
    """`[rig] workspace`, resolved against the description's folder."""
    source = Path(path)
    rig = read_rig(table_at(read_toml_file(source), "rig", str(source)), source)
    if rig.workspace is None:
        raise ValueError(f"{source}: [rig] workspace is required")
    return rig.workspace
