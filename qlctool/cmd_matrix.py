"""`qlctool matrix`: generate RGBMatrix effects (algorithm x colour) into a copy of the workspace."""

import argparse
from pathlib import Path

from .constants import ALL_FIXTURES_GROUP
from .default_out import default_out
from .finish import finish
from .generate.generate_matrix_effects import generate_matrix_effects
from .lay_out import lay_out
from .matrix_algorithms import SCRIPT_ALGORITHMS
from .workspace import Workspace


def cmd_matrix(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else default_out(src)

    algorithms: list[str | None] = (
        [None if a.lower() == "solid" else a for a in args.algorithms.split(",") if a]
        if args.algorithms
        else list(SCRIPT_ALGORITHMS)
    )
    group_id = ALL_FIXTURES_GROUP if args.group.lower() == "all" else int(args.group)

    ws = Workspace.load(src)
    result = generate_matrix_effects(
        ws,
        group_id=group_id,
        algorithms=algorithms,
        make_chaser=not args.no_chaser,
    )
    created = result.matrix_ids + ([] if result.chaser_id is None else [result.chaser_id])
    lay_out(ws, created, args.buttons)
    ws.save(out)

    print(
        f"Generated {len(result.matrix_ids)} RGBMatrix functions"
        + ("" if result.chaser_id is None else " + 1 cycle chaser")
    )
    return finish(out, args.validate)
