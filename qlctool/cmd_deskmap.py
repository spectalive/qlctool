"""`qlctool deskmap`: write the tablet desk's map for a saved workspace."""

import argparse
import json
from pathlib import Path

from .build_deskmap import build_deskmap
from .description.description_names import description_names
from .description.load_show_description import load_show_description
from .library_for import library_for
from .unresolved_fixtures import unresolved_fixtures
from .warn_unresolved import warn_unresolved
from .workspace import Workspace


def cmd_deskmap(args: argparse.Namespace) -> int:
    workspace = Workspace.load(args.workspace)
    library = library_for(args.fixtures, Path(args.workspace))
    warn_unresolved(workspace.root, library)
    if unresolved_fixtures(workspace.root, library):
        # A control keyed to a fixture with no definition is left out rather
        # than guessed, so a map built this way is missing entries with no
        # other signal than the warning above (M-2, 2026-09-27 final review).
        return 2
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
