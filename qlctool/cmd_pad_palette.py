"""`qlctool pad-palette`: write the SMC-PAD LED bridge's palette for a saved workspace."""

import argparse
import json
from pathlib import Path

from .build_pad_palette import build_pad_palette
from .workspace import Workspace


def cmd_pad_palette(args: argparse.Namespace) -> int:
    palette = build_pad_palette(Workspace.load(args.workspace), args.workspace)
    out = Path(args.out)
    text = json.dumps(palette, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    out.write_text(text, encoding="utf-8")
    lit = sum(1 for pad in palette["pads"] if pad["control"] is not None)
    print(f"{out}: {len(palette['pads'])} pads, {lit} lit")
    return 0
