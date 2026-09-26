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


def add_pad_palette_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    parser = sub.add_parser(
        "pad-palette",
        help="write the SMC-PAD LED bridge's palette: each pad's note and colours from the saved show",
    )
    parser.add_argument("workspace")
    parser.add_argument("--out", required=True, help="the JSON file to write")
    parser.set_defaults(func=cmd_pad_palette)
