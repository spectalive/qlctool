"""Command-line entry point for qlctool.

Thin wrapper over the library so the owner can run generators without writing
Python: inspect a workspace, or generate a colour palette + cycle chaser into a
copy. Never overwrites the input - it always writes a new file.
"""

import argparse
from pathlib import Path

from .capabilities_of import capabilities_of
from .compose import compose_workspace
from .constants import ALL_FIXTURES_GROUP
from .decompose import decompose_workspace
from .efx_algorithms import EFX_ALGORITHMS
from .fixture_group import fixture_groups
from .generate.canonical_show import build_canonical_show
from .generate.channel_probe import generate_channel_probe
from .generate.color_palette import generate_color_palette
from .generate.matrix_effects import generate_matrix_effects
from .generate.movement_efx import generate_movement_efx
from .generate.vc_layout import generate_vc_layout
from .matrix_algorithms import SCRIPT_ALGORITHMS
from .library import FixtureLibrary
from .patch_conflicts import patch_conflicts
from .repatch.add import add_fixture
from .repatch.address import set_fixture_address
from .repatch.remove import remove_fixture
from .repatch.rename import rename_fixture
from .validate import validate_workspace
from .workspace import Workspace


def _default_out(src: Path) -> Path:
    return src.with_name(f"{src.stem}-generado{src.suffix}")


def _lay_out(ws: Workspace, function_ids: list[int], wanted: bool) -> None:
    """Add Virtual Console buttons for functions we just created, on request."""
    if not wanted or not function_ids:
        return
    layout = generate_vc_layout(ws, function_ids=function_ids)
    print(f"Laid out {len(layout.button_ids)} Virtual Console buttons "
          f"in {len(layout.frame_ids)} frame(s)")


def _finish(out: Path, validate: bool) -> int:
    """Report where the file went and, on request, that QLC+ accepts it."""
    print(f"Wrote {out}")
    if not validate:
        print("Open it in QLC+ to verify before using it in a show.")
        return 0
    result = validate_workspace(out)
    if result.ok:
        print("Validated: QLC+ loaded it with no complaints")
        return 0
    print("QLC+ reported problems loading it:")
    for error in result.errors:
        print(f"  {error}")
    return 1


def cmd_info(args: argparse.Namespace) -> int:
    ws = Workspace.load(args.workspace)
    library = FixtureLibrary.load()
    caps = capabilities_of(ws.root, library)
    print(f"{args.workspace}: {len(caps)} fixtures with resolved capabilities")
    for c in caps:
        f = c.fixture
        role_summary = ", ".join(sorted(c.roles)) or "(no driven roles)"
        print(f"  [{f.fixture_id:>3}] U{f.universe} @{f.address + 1:<4} "
              f"{f.manufacturer}/{f.model} <{f.mode}>: {role_summary}")
    groups = fixture_groups(ws.root)
    print(f"{len(groups)} fixture groups (RGBMatrix targets):")
    for g in groups:
        print(f"  [{g.group_id}] {g.name}: {g.width}x{g.height} grid, "
              f"{g.head_count} heads")
    return 0


def cmd_palette(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else _default_out(src)

    ws = Workspace.load(src)
    library = FixtureLibrary.load()
    result = generate_color_palette(ws, library, make_chaser=not args.no_chaser)
    created = result.scene_ids + ([] if result.chaser_id is None else [result.chaser_id])
    _lay_out(ws, created, args.buttons)
    ws.save(out)

    print(f"Generated {len(result.scene_ids)} colour scenes"
          + ("" if result.chaser_id is None else " + 1 cycle chaser"))
    return _finish(out, args.validate)


def cmd_matrix(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else _default_out(src)

    algorithms: list[str | None] = (
        [None if a.lower() == "solid" else a
         for a in args.algorithms.split(",") if a]
        if args.algorithms else list(SCRIPT_ALGORITHMS)
    )
    group_id = (
        ALL_FIXTURES_GROUP if args.group.lower() == "all" else int(args.group)
    )

    ws = Workspace.load(src)
    result = generate_matrix_effects(
        ws,
        group_id=group_id,
        algorithms=algorithms,
        make_chaser=not args.no_chaser,
    )
    created = result.matrix_ids + ([] if result.chaser_id is None else [result.chaser_id])
    _lay_out(ws, created, args.buttons)
    ws.save(out)

    print(f"Generated {len(result.matrix_ids)} RGBMatrix functions"
          + ("" if result.chaser_id is None else " + 1 cycle chaser"))
    return _finish(out, args.validate)


def cmd_movement(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else _default_out(src)

    algorithms = (
        [a for a in args.algorithms.split(",") if a]
        if args.algorithms else list(EFX_ALGORITHMS)
    )

    ws = Workspace.load(src)
    result = generate_movement_efx(
        ws,
        FixtureLibrary.load(),
        algorithms=algorithms,
        propagation_mode=args.propagation,
        make_chaser=not args.no_chaser,
    )
    created = result.efx_ids + ([] if result.chaser_id is None else [result.chaser_id])
    _lay_out(ws, created, args.buttons)
    ws.save(out)

    print(f"Generated {len(result.efx_ids)} movement EFX"
          + ("" if result.chaser_id is None else " + 1 cycle chaser"))
    return _finish(out, args.validate)


def cmd_patch(args: argparse.Namespace) -> int:
    """Inspect or edit the patch. Addresses on the command line are 1-based,
    the way QLC+ shows them; the file stores them 0-based."""
    src = Path(args.workspace)
    ws = Workspace.load(src)

    edits = args.add or args.set_address or args.rename or args.remove
    if not edits:
        conflicts = patch_conflicts(ws.root)
        if not conflicts:
            print(f"{src}: patch is clean, no address overlaps")
            return 0
        print(f"{src}: {len(conflicts)} address overlap(s)")
        for conflict in conflicts:
            print(f"  {conflict.describe()}")
        return 1

    library = FixtureLibrary.load()
    for spec in args.add or []:
        parts = spec.split("|")
        if len(parts) not in (5, 6):
            raise SystemExit(
                "--add takes Manufacturer|Model|Mode|universe|address[|name]"
            )
        manufacturer, model, mode, universe, address = parts[:5]
        name = parts[5] if len(parts) == 6 else None
        fixture_id = add_fixture(
            ws.root, library, manufacturer, model, mode,
            universe=int(universe), address=int(address) - 1, name=name,
        )
        print(f"added [{fixture_id}] {manufacturer}/{model} <{mode}> "
              f"at U{universe} @{address}")

    for spec in args.set_address or []:
        target, placement = spec.split("=", 1)
        universe, address = placement.split(":", 1)
        set_fixture_address(
            ws.root, int(target), int(address) - 1, universe=int(universe)
        )
        print(f"re-addressed [{target}] to U{universe} @{address}")

    for spec in args.rename or []:
        target, name = spec.split("=", 1)
        previous = rename_fixture(ws.root, int(target), name)
        print(f"renamed [{target}] {previous!r} -> {name!r}")

    for target in args.remove or []:
        cleared = remove_fixture(ws.root, target)
        print(f"removed [{target}] and {cleared} reference(s) to it")

    remaining = patch_conflicts(ws.root)
    for conflict in remaining:
        print(f"WARNING overlap: {conflict.describe()}")

    out = Path(args.out) if args.out else _default_out(src)
    ws.save(out)
    return _finish(out, args.validate)


def cmd_newshow(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else src.with_name("Vibra.qxw")

    ws = Workspace.load(src)
    show = build_canonical_show(
        ws, FixtureLibrary.load(), with_layout=not args.no_buttons
    )
    ws.save(out)

    colors = sum(len(b.scene_ids) + len(b.split_ids) for b in show.banks)
    print(f"Built a self-running show on the same patch: {show.function_count} "
          f"functions ({colors} colour scenes across {len(show.banks)} groups, "
          f"{len(show.matrix_ids)} matrices, {len(show.efx_ids)} movement EFX, "
          f"{len(show.gobo_ids)} gobos, {len(show.prism_ids)} prism, plus "
          f"dimmer chase, ping-pong and strobes), "
          f"{len(show.button_ids)} console buttons on one 1440x900 screen. "
          f"Press AUTO (key Q).")
    return _finish(out, args.validate)


def cmd_probe(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else _default_out(src)

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
    _lay_out(ws, result.scene_ids + [result.chaser_id], args.buttons)
    ws.save(out)

    print(f"Generated {len(result.scene_ids)} probe scenes for fixture "
          f"{args.fixture} + 1 walk chaser")
    return _finish(out, args.validate)


def cmd_layout(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else _default_out(src)

    ws = Workspace.load(src)
    layout = generate_vc_layout(ws, columns=args.columns)
    ws.save(out)

    print(f"Laid out {len(layout.button_ids)} buttons "
          f"in {len(layout.frame_ids)} frame(s)")
    return _finish(out, args.validate)


def cmd_validate(args: argparse.Namespace) -> int:
    result = validate_workspace(args.workspace)
    if result.ok:
        print(f"{args.workspace}: QLC+ loaded it with no complaints")
        return 0
    print(f"{args.workspace}: QLC+ reported {len(result.errors)} problem(s)")
    for error in result.errors:
        print(f"  {error}")
    return 1


def cmd_decompose(args: argparse.Namespace) -> int:
    decompose_workspace(args.workspace, args.out_dir)
    print(f"Decomposed {args.workspace} -> {args.out_dir}/ "
          "(skeleton.qxw, functions/, manifest.json)")
    return 0


def cmd_compose(args: argparse.Namespace) -> int:
    compose_workspace(args.src_dir, args.out)
    print(f"Composed {args.src_dir}/ -> {args.out}")
    return _finish(Path(args.out), args.validate)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qlctool", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_info = sub.add_parser("info", help="list patched fixtures and their roles")
    p_info.add_argument("workspace")
    p_info.set_defaults(func=cmd_info)

    p_pal = sub.add_parser("palette", help="generate colour scenes + cycle chaser")
    p_pal.add_argument("workspace")
    p_pal.add_argument("--out", help="output file (default: <name>-generado.qxw)")
    p_pal.add_argument("--no-chaser", action="store_true",
                       help="scenes only, skip the cycle chaser")
    p_pal.add_argument("--buttons", action="store_true",
                       help="also add Virtual Console buttons for what was "
                            "generated")
    p_pal.add_argument("--validate", action="store_true",
                       help="load the result in headless QLC+ and fail on "
                            "any problem it reports")
    p_pal.set_defaults(func=cmd_palette)

    p_mat = sub.add_parser(
        "matrix", help="generate RGBMatrix effects (algorithm x colour)"
    )
    p_mat.add_argument("workspace")
    p_mat.add_argument("--group", default="all",
                       help="fixture group ID to paint, or 'all' (default)")
    p_mat.add_argument("--algorithms",
                       help="comma-separated RGB script names, 'solid' for a "
                            "plain colour matrix (default: all known scripts)")
    p_mat.add_argument("--out", help="output file (default: <name>-generado.qxw)")
    p_mat.add_argument("--no-chaser", action="store_true",
                       help="matrices only, skip the cycle chaser")
    p_mat.add_argument("--buttons", action="store_true",
                       help="also add Virtual Console buttons for what was "
                            "generated")
    p_mat.add_argument("--validate", action="store_true",
                       help="load the result in headless QLC+ and fail on "
                            "any problem it reports")
    p_mat.set_defaults(func=cmd_matrix)

    p_mov = sub.add_parser(
        "movement", help="generate movement EFX across every moving head"
    )
    p_mov.add_argument("workspace")
    p_mov.add_argument("--algorithms",
                       help="comma-separated EFX algorithms "
                            f"(default: {','.join(EFX_ALGORITHMS)})")
    p_mov.add_argument("--propagation", default="Parallel",
                       choices=["Parallel", "Serial", "Asymmetric"])
    p_mov.add_argument("--out", help="output file (default: <name>-generado.qxw)")
    p_mov.add_argument("--no-chaser", action="store_true",
                       help="EFX only, skip the cycle chaser")
    p_mov.add_argument("--buttons", action="store_true",
                       help="also add Virtual Console buttons for what was "
                            "generated")
    p_mov.add_argument("--validate", action="store_true",
                       help="load the result in headless QLC+ and fail on "
                            "any problem it reports")
    p_mov.set_defaults(func=cmd_movement)

    p_patch = sub.add_parser(
        "patch",
        help="check the patch for address overlaps, or edit it "
             "(add/re-address/rename/remove)",
    )
    p_patch.add_argument("workspace")
    p_patch.add_argument("--add", action="append", metavar="SPEC",
                         help="Manufacturer|Model|Mode|universe|address[|name], "
                              "address 1-based")
    p_patch.add_argument("--set-address", action="append", metavar="ID=U:A",
                         help="move fixture ID to universe U, address A "
                              "(1-based)")
    p_patch.add_argument("--rename", action="append", metavar="ID=NAME")
    p_patch.add_argument("--remove", action="append", type=int, metavar="ID",
                         help="unpatch fixture ID and clear every reference")
    p_patch.add_argument("--out", help="output file (default: <name>-generado.qxw)")
    p_patch.add_argument("--validate", action="store_true",
                       help="load the result in headless QLC+ and fail on "
                            "any problem it reports")
    p_patch.set_defaults(func=cmd_patch)

    p_new = sub.add_parser(
        "newshow",
        help="build a fresh show on an existing patch: strip the functions, "
             "generate palette + matrices + movement + console",
    )
    p_new.add_argument("workspace", help="the show to take the patch from")
    p_new.add_argument("--out", help="output file (default: Vibra.qxw beside it)")
    p_new.add_argument("--no-buttons", action="store_true",
                       help="skip the Virtual Console layout")
    p_new.add_argument("--validate", action="store_true",
                       help="load the result in QLC+ and fail on any problem")
    p_new.set_defaults(func=cmd_newshow)

    p_prb = sub.add_parser(
        "probe",
        help="one scene per DMX channel of a fixture, to find out on site what "
             "each channel does",
    )
    p_prb.add_argument("workspace")
    p_prb.add_argument("fixture", type=int, help="fixture ID (see `qlctool info`)")
    p_prb.add_argument("--value", type=int, default=255,
                       help="value to drive the channel under test (default 255)")
    p_prb.add_argument("--base", metavar="CH=VAL,...",
                       help="channels to hold steady while probing, 1-based "
                            "(e.g. a dimmer that must be open: 7=255)")
    p_prb.add_argument("--hold", type=int, default=3000,
                       help="ms per step in the walk chaser (default 3000)")
    p_prb.add_argument("--buttons", action="store_true",
                       help="also add Virtual Console buttons")
    p_prb.add_argument("--out", help="output file (default: <name>-generado.qxw)")
    p_prb.add_argument("--validate", action="store_true",
                       help="load the result in QLC+ and fail on any problem")
    p_prb.set_defaults(func=cmd_probe)

    p_lay = sub.add_parser(
        "layout",
        help="add Virtual Console buttons for every function that has a folder",
    )
    p_lay.add_argument("workspace")
    p_lay.add_argument("--columns", type=int, default=6,
                       help="buttons per row (default 6)")
    p_lay.add_argument("--out", help="output file (default: <name>-generado.qxw)")
    p_lay.add_argument("--validate", action="store_true",
                       help="load the result in QLC+ and fail on any problem")
    p_lay.set_defaults(func=cmd_layout)

    p_val = sub.add_parser(
        "validate", help="load a workspace in headless QLC+ and report problems"
    )
    p_val.add_argument("workspace")
    p_val.set_defaults(func=cmd_validate)

    p_dec = sub.add_parser(
        "decompose", help="split a workspace into a git-diffable fragment tree"
    )
    p_dec.add_argument("workspace")
    p_dec.add_argument("out_dir")
    p_dec.set_defaults(func=cmd_decompose)

    p_com = sub.add_parser(
        "compose", help="rebuild a workspace from a fragment tree"
    )
    p_com.add_argument("src_dir")
    p_com.add_argument("out")
    p_com.add_argument("--validate", action="store_true",
                       help="load the result in headless QLC+ and fail on "
                            "any problem it reports")
    p_com.set_defaults(func=cmd_compose)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
