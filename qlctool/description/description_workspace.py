"""The workspace a description's [rig] names, needed before the rest can be validated."""

from pathlib import Path

from .reading.read_rig import read_rig
from .reading.read_toml_file import read_toml_file
from .reading.table_at import table_at


def description_workspace(path: str | Path) -> Path:
    """`[rig] workspace`, resolved against the description's folder."""
    source = Path(path)
    workspace = read_rig(table_at(read_toml_file(source), "rig", str(source)), source).workspace
    # read_rig refuses a [rig] without a workspace, so this only narrows the type.
    assert workspace is not None
    return workspace
