"""`qlctool probe`: one scene per DMX channel of a fixture, for on-site channel discovery."""

import argparse
from pathlib import Path

from .default_out import default_out
from .finish import finish
from .generate.generate_channel_probe import generate_channel_probe
from .lay_out import lay_out
from .workspace import Workspace


def cmd_probe(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else default_out(src)

    base = {}
    for pair in (args.base or "").split(","):
        if not pair:
            continue
        channel, value = pair.split("=", 1)
        base[int(channel) - 1] = int(value)

    ws = Workspace.load(src)
    result = generate_channel_probe(
        ws, args.fixture, value=args.value, base_values=base, hold=args.hold
    )
    created = result.scene_ids + ([] if result.chaser_id is None else [result.chaser_id])
    lay_out(ws, created, args.buttons)
    ws.save(out)

    print(
        f"Generated {len(result.scene_ids)} probe scenes for fixture {args.fixture} + 1 walk chaser"
    )
    return finish(out, args.validate)
