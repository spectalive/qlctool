"""`qlctool stage`: place every fixture in the 2D/3D view, a row per band or from a written plot."""

import argparse
from pathlib import Path

from .beam_landing import beam_landing
from .capabilities_of import capabilities_of
from .default_out import default_out
from .finish import finish
from .generate.apply_stage_plot import apply_stage_plot
from .generate.generate_stage_layout import generate_stage_layout
from .library_for import library_for
from .load_stage_plot import load_stage_plot
from .stage_size import stage_size
from .warn_unresolved import warn_unresolved
from .workspace import Workspace


def cmd_stage(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else default_out(src)

    ws = Workspace.load(src)
    library = library_for(args.fixtures, src)
    warn_unresolved(ws.root, library)
    if args.plot:
        plot = apply_stage_plot(ws, load_stage_plot(args.plot, ws.root))
        ws.save(out)
        print(
            f"Applied {plot.name!r}: {len(plot.rigged)} fixtures rigged, "
            f"{len(plot.spare)} spare and hidden, on a "
            f"{plot.stage[0]}x{plot.stage[1]}x{plot.stage[2]} m stage seen "
            f"from the {plot.point_of_view}."
        )
        # Where each beam ends up, because an angle that looks right in the
        # preview can still be putting the light on the DJ's face.
        caps = {c.fixture.fixture_id: c for c in capabilities_of(ws.root, library)}
        for item in sorted(plot.items, key=lambda i: i.fixture_id):
            if item.hidden or item.fixture_id not in caps:
                continue
            landing = beam_landing(item, caps[item.fixture_id])
            where = f"floor at z={landing.z:.0f}" if landing.z is not None else landing.reason
            print(f"  [{item.fixture_id:>2}] {plot.places[item.fixture_id]}\n       {where}")
        return finish(out, args.validate)

    stage = generate_stage_layout(
        ws,
        library,
        stage=stage_size(args.stage),
        point_of_view=args.pov,
    )
    ws.save(out)

    print(
        f"Placed {stage.placed} fixtures on a "
        f"{stage.stage[0]}x{stage.stage[1]}x{stage.stage[2]} m stage, "
        f"seen from the {stage.point_of_view}:"
    )
    for band, fixture_ids in stage.rows.items():
        print(f"  {band:<7} {len(fixture_ids)}: {fixture_ids}")
    return finish(out, args.validate)
