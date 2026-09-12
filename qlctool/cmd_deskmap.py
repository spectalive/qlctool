"""`qlctool deskmap`: write the tablet desk's map for a saved workspace."""

import argparse
import json
from pathlib import Path

from .deskmap import build_deskmap
from .library import FixtureLibrary
from .workspace import Workspace


def cmd_deskmap(args: argparse.Namespace) -> int:
    workspace = Workspace.load(args.workspace)
    deskmap = build_deskmap(workspace, FixtureLibrary.load(), args.workspace)
    out = Path(args.out)
    out.write_text(json.dumps(deskmap, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    enabled = sum(1 for c in deskmap["controls"].values() if c["enabled"])
    print(f"{out}: {len(deskmap['controls'])} controles, {enabled} activos, {len(deskmap['dials'])} diales")
    for page in deskmap["pages"]:
        parts = ", ".join(f"{s['key']} {len(s['controls'])}" for s in page["sections"])
        print(f"  {page['key']}: {parts}")
    return 0


def add_deskmap_parser(sub) -> None:
    parser = sub.add_parser(
        "deskmap",
        help="write the tablet desk's map: pages, controls, swatches and dials from the saved show",
    )
    parser.add_argument("workspace")
    parser.add_argument("--out", required=True, help="the JSON file to write")
    parser.set_defaults(func=cmd_deskmap)
