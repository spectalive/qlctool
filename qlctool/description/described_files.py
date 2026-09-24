"""The patch `newshow --description` reads and the file it writes."""

from pathlib import Path

from .reading.read_rig import read_rig
from .reading.read_toml_file import read_toml_file
from .reading.table_at import table_at


def described_files(
    workspace: str | None, description: str | Path, out: str | None
) -> tuple[Path, Path]:
    """(patch, output) for a description, never the patch file by accident.

    The output is `out`, else `[rig] output`; with neither, this refuses rather
    than overwrite the patch. A positional workspace must be the one `[rig]`
    names, so a command line cannot quietly pair a description with another patch.
    """
    source = Path(description)
    rig = read_rig(table_at(read_toml_file(source), "rig", str(source)), source)
    # read_rig refuses a [rig] without a workspace, so this only narrows the type.
    assert rig.workspace is not None
    if workspace is not None and Path(workspace).resolve() != rig.workspace.resolve():
        raise ValueError(
            f"{source}: [rig] workspace is {rig.workspace}, but the command line names "
            f"{workspace}; leave the workspace out, or state it in [rig]"
        )
    if out is not None:
        return rig.workspace, Path(out)
    if rig.output is None:
        raise ValueError(
            f"{source}: [rig] states no output and --out was not given, and newshow never "
            "overwrites the patch unasked; state [rig] output (equal to workspace to "
            "regenerate it in place) or pass --out"
        )
    return rig.workspace, rig.output
