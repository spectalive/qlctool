"""`qlctool layout`: add Virtual Console buttons for every function that has a folder."""

import argparse
from pathlib import Path

from .default_out import default_out
from .finish import finish
from .generate.generate_vc_layout import generate_vc_layout
from .workspace import Workspace


def cmd_layout(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else default_out(src)

    ws = Workspace.load(src)
    layout = generate_vc_layout(ws, columns=args.columns)
    ws.save(out)

    print(f"Laid out {len(layout.button_ids)} buttons in {len(layout.frame_ids)} frame(s)")
    return finish(out, args.validate)
