"""`qlctool patch`: check the patch for address overlaps, or edit it."""

import argparse
from pathlib import Path

from .default_out import default_out
from .finish import finish
from .library_for import library_for
from .patch_conflicts import patch_conflicts
from .repatch.add_fixture import add_fixture
from .repatch.add_fixture_group import add_fixture_group
from .repatch.add_group_head import add_group_head
from .repatch.move_group_head import move_group_head
from .repatch.remove_fixture import remove_fixture
from .repatch.remove_group_head import remove_group_head
from .repatch.rename_fixture import rename_fixture
from .repatch.reshape_group import reshape_group
from .repatch.set_fixture_address import set_fixture_address
from .repatch.set_group_size import set_group_size
from .repatch.sort_group_by_stage import sort_group_by_stage
from .warn_unresolved import warn_unresolved
from .workspace import Workspace


def cmd_patch(args: argparse.Namespace) -> int:
    """Inspect or edit the patch. Addresses on the command line are 1-based,
    the way QLC+ shows them; the file stores them 0-based.
    """
    src = Path(args.workspace)
    ws = Workspace.load(src)

    edits = (
        args.add
        or args.set_address
        or args.rename
        or args.remove
        or args.group_size
        or args.group_add
        or args.group_remove
        or args.group_move
        or args.group_sort
        or args.group_new
        or args.group_reshape
    )
    if not edits:
        conflicts = patch_conflicts(ws.root)
        if not conflicts:
            print(f"{src}: patch is clean, no address overlaps")
            return 0
        print(f"{src}: {len(conflicts)} address overlap(s)")
        for conflict in conflicts:
            print(f"  {conflict.describe()}")
        return 1

    library = library_for(args.fixtures, src)
    warn_unresolved(ws.root, library)
    for spec in args.add or []:
        parts = spec.split("|")
        if len(parts) not in (5, 6):
            raise SystemExit("--add takes Manufacturer|Model|Mode|universe|address[|name]")
        manufacturer, model, mode, universe, address = parts[:5]
        name = parts[5] if len(parts) == 6 else None
        fixture_id = add_fixture(
            ws.root,
            library,
            manufacturer,
            model,
            mode,
            universe=int(universe),
            address=int(address) - 1,
            name=name,
        )
        print(f"added [{fixture_id}] {manufacturer}/{model} <{mode}> at U{universe} @{address}")

    for spec in args.set_address or []:
        target, placement = spec.split("=", 1)
        universe, address = placement.split(":", 1)
        set_fixture_address(ws.root, int(target), int(address) - 1, universe=int(universe))
        print(f"re-addressed [{target}] to U{universe} @{address}")

    for spec in args.rename or []:
        target, name = spec.split("=", 1)
        previous = rename_fixture(ws.root, int(target), name)
        print(f"renamed [{target}] {previous!r} -> {name!r}")

    for target in args.remove or []:
        cleared = remove_fixture(ws.root, target)
        print(f"removed [{target}] and {cleared} reference(s) to it")

    # Grid before members: a cell outside the declared size is a head no effect
    # can reach, so add_group_head refuses it.
    for spec in args.group_new or []:
        name, size = spec.split("=", 1)
        width, height = size.lower().split("x", 1)
        new_id = add_fixture_group(ws.root, name, int(width), int(height))
        print(f"fixture group {new_id} {name!r} created, {width}x{height}, empty")

    for spec in args.group_size or []:
        group, size = spec.split("=", 1)
        width, height = size.lower().split("x", 1)
        set_group_size(ws.root, int(group), int(width), int(height))
        print(f"group {group} grid is now {width}x{height}")

    for spec in args.group_add or []:
        group, placement = spec.split("=", 1)
        fixture, cell = placement.split("@", 1)
        fixture, _, head = fixture.partition(":")
        x, y = cell.split(",", 1)
        add_group_head(
            ws.root,
            int(group),
            int(fixture),
            int(x),
            int(y),
            int(head or 0),
        )
        print(f"group {group} cell ({x},{y}) now holds fixture {fixture} head {head or 0}")

    for spec in args.group_sort or []:
        moved = sort_group_by_stage(ws.root, int(spec))
        print(
            f"group {spec} re-laid in stage order, {len(moved)} cell(s) moved"
            if moved
            else f"group {spec} was already in stage order"
        )

    for spec in args.group_move or []:
        group, placement = spec.split("=", 1)
        fixture, cell = placement.split("@", 1)
        fixture, _, head = fixture.partition(":")
        x, y = cell.split(",", 1)
        was = move_group_head(
            ws.root,
            int(group),
            int(fixture),
            int(x),
            int(y),
            int(head or 0),
        )
        print(f"group {group}: fixture {fixture} head {head or 0} moved from {was} to ({x},{y})")

    for spec in args.group_remove or []:
        group, fixture = spec.split("=", 1)
        removed = remove_group_head(ws.root, int(group), int(fixture))
        print(f"group {group} lost {removed} head(s) of fixture {fixture}")

    for spec in args.group_reshape or []:
        group, size = spec.split("=", 1)
        width, height = size.lower().split("x", 1)
        reshape_group(ws.root, int(group), int(width), int(height))
        print(f"group {group} re-laid into {width}x{height}, no holes")

    remaining = patch_conflicts(ws.root)
    for conflict in remaining:
        print(f"WARNING overlap: {conflict.describe()}")

    out = Path(args.out) if args.out else default_out(src)
    ws.save(out)
    return finish(out, args.validate)
