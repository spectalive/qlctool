"""`qlctool palette`: generate colour scenes + cycle chaser into a copy of the workspace."""

import argparse
from pathlib import Path

from .default_out import default_out
from .finish import finish
from .generate.generate_color_palette import generate_color_palette
from .lay_out import lay_out
from .library_for import library_for
from .warn_unresolved import warn_unresolved
from .workspace import Workspace


def cmd_palette(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else default_out(src)

    ws = Workspace.load(src)
    library = library_for(args.fixtures, src)
    warn_unresolved(ws.root, library)
    result = generate_color_palette(ws, library, make_chaser=not args.no_chaser)
    created = result.scene_ids + ([] if result.chaser_id is None else [result.chaser_id])
    lay_out(ws, created, args.buttons)
    ws.save(out)

    print(
        f"Generated {len(result.scene_ids)} colour scenes"
        + ("" if result.chaser_id is None else " + 1 cycle chaser")
    )
    return finish(out, args.validate)
