"""`qlctool info`: list a workspace's patched fixtures and their resolved roles."""

import argparse
from pathlib import Path

from .capabilities_of import capabilities_of
from .fixture_groups import fixture_groups
from .library_for import library_for
from .warn_unresolved import warn_unresolved
from .workspace import Workspace


def cmd_info(args: argparse.Namespace) -> int:
    ws = Workspace.load(args.workspace)
    library = library_for(args.fixtures, Path(args.workspace))
    warn_unresolved(ws.root, library)
    caps = capabilities_of(ws.root, library)
    print(f"{args.workspace}: {len(caps)} fixtures with resolved capabilities")
    for c in caps:
        f = c.fixture
        role_summary = ", ".join(sorted(c.roles)) or "(no driven roles)"
        print(
            f"  [{f.fixture_id:>3}] U{f.universe} @{f.address + 1:<4} "
            f"{f.manufacturer}/{f.model} <{f.mode}>: {role_summary}"
        )
    groups = fixture_groups(ws.root)
    print(f"{len(groups)} fixture groups (RGBMatrix targets):")
    for g in groups:
        print(f"  [{g.group_id}] {g.name}: {g.width}x{g.height} grid, {g.head_count} heads")
    return 0
