"""`qlctool mvr`: export the placed rig as an MVR package with a GDTF per definition."""

import argparse
from pathlib import Path

from .library_for import library_for
from .mvr.write_mvr import write_mvr
from .warn_unresolved import warn_unresolved
from .workspace import Workspace


def cmd_mvr(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else src.with_suffix(".mvr")
    gobos = Path(args.gobos) if args.gobos else src.parent / "Gobos"
    ws = Workspace.load(src)
    library = library_for(args.fixtures, src)
    warn_unresolved(ws.root, library)
    export = write_mvr(ws, library, out, gobos)
    print(
        f"Wrote {export.path}: {len(export.fixtures)} fixtures placed, "
        f"{len(export.gdtf_files)} GDTF fixture types inside."
    )
    for name in export.gdtf_files:
        print(f"  {name}")
    for name, why in export.skipped.items():
        print(f"  skipped {name}: {why}")
    return 0
