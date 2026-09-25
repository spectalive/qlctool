"""`qlctool deskmap`: write the tablet desk's map for a saved workspace."""

import argparse
import json
from pathlib import Path

from .description.description_names import description_names
from .description.load_show_description import load_show_description
from .deskmap import build_deskmap
from .library_for import library_for
from .warn_unresolved import warn_unresolved
from .workspace import Workspace


def cmd_deskmap(args: argparse.Namespace) -> int:
    workspace = Workspace.load(args.workspace)
    library = library_for(args.fixtures, Path(args.workspace))
    warn_unresolved(workspace.root, library)
    names = None
    if args.description:
        names = description_names(load_show_description(args.description, workspace.root))
    deskmap = build_deskmap(workspace, library, args.workspace, names=names)
    out = Path(args.out)
    out.write_text(json.dumps(deskmap, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    enabled = sum(1 for c in deskmap["controls"].values() if c["enabled"])
    print(
        f"{out}: {len(deskmap['controls'])} controles, {enabled} activos, {len(deskmap['dials'])} diales"
    )
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
    parser.add_argument(
        "--description",
        help="the show description whose language and names the map uses "
        "(default: the language the workspace was generated in)",
    )
    parser.set_defaults(func=cmd_deskmap)
