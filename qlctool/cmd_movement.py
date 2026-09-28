"""`qlctool movement`: generate movement EFX across every moving head into a copy of the workspace."""

import argparse
from pathlib import Path

from .default_out import default_out
from .efx_algorithms import EFX_ALGORITHMS
from .finish import finish
from .generate.generate_movement_efx import generate_movement_efx
from .lay_out import lay_out
from .library_for import library_for
from .warn_unresolved import warn_unresolved
from .workspace import Workspace


def cmd_movement(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else default_out(src)

    algorithms = (
        [a for a in args.algorithms.split(",") if a] if args.algorithms else list(EFX_ALGORITHMS)
    )

    ws = Workspace.load(src)
    library = library_for(args.fixtures, src)
    warn_unresolved(ws.root, library)
    result = generate_movement_efx(
        ws,
        library,
        algorithms=algorithms,
        propagation_mode=args.propagation,
        make_chaser=not args.no_chaser,
    )
    created = result.efx_ids + ([] if result.chaser_id is None else [result.chaser_id])
    lay_out(ws, created, args.buttons)
    ws.save(out)

    print(
        f"Generated {len(result.efx_ids)} movement EFX"
        + ("" if result.chaser_id is None else " + 1 cycle chaser")
    )
    return finish(out, args.validate)
