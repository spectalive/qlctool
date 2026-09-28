"""Command-line entry point for qlctool.

Thin wrapper over the library so the owner can run generators without writing
Python: inspect a workspace, or generate a colour palette + cycle chaser into a
copy. Never overwrites the input - it always writes a new file.
"""

import argparse
from dataclasses import replace
from pathlib import Path

from .add_check_parser import add_check_parser
from .add_deskmap_parser import add_deskmap_parser
from .add_info_parser import add_info_parser
from .add_layout_parser import add_layout_parser
from .add_matrix_parser import add_matrix_parser
from .add_mcp_parser import add_mcp_parser
from .add_movement_parser import add_movement_parser
from .add_newshow_parser import add_newshow_parser
from .add_pad_palette_parser import add_pad_palette_parser
from .add_palette_parser import add_palette_parser
from .add_patch_parser import add_patch_parser
from .add_probe_parser import add_probe_parser
from .add_stage_parser import add_stage_parser
from .apply_install import apply_install
from .compose_workspace import compose_workspace
from .decompose_workspace import decompose_workspace
from .finish import finish
from .fixture_dirs import fixture_dirs
from .generate.input_profile import build_input_profile
from .install_plan import install_plan
from .library_for import library_for
from .mvr.write_mvr import write_mvr
from .qlc_gobo_dir import qlc_gobo_dir
from .qlc_user_dir import qlc_user_dir
from .toolkit_config_from import toolkit_config_from
from .validate_workspace import validate_workspace
from .warn_unresolved import warn_unresolved
from .workspace import Workspace


def cmd_mvr(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else src.with_suffix(".mvr")
    gobos = Path(args.gobos) if args.gobos else src.parent / "Gobos"
    ws = Workspace.load(src)
    library = library_for(args.fixtures, src)
    warn_unresolved(ws.root, library)
    export = write_mvr(ws, library, out, gobos)
    print(
        f"Wrote {export.path}: {len(export.fixtures)} fixtures placed, "
        f"{len(export.gdtf_files)} GDTF fixture types inside."
    )
    for name in export.gdtf_files:
        print(f"  {name}")
    for name, why in export.skipped.items():
        print(f"  skipped {name}: {why}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    result = validate_workspace(args.workspace)
    if result.ok:
        print(f"{args.workspace}: QLC+ loaded it with no complaints")
        return 0
    print(f"{args.workspace}: QLC+ reported {len(result.errors)} problem(s)")
    for error in result.errors:
        print(f"  {error}")
    return 1


def cmd_install(args: argparse.Namespace) -> int:
    """Hand QLC+ the configured definitions, profile and gobos - or say what it lacks.

    The fixture folders follow ruling B3 (`--fixtures`, QLCTOOL_FIXTURES, then
    the nearest qlctool.toml); the profiles and gobos come from qlctool.toml.
    A definition the repo fixed and QLC+ never received is the silent failure
    this exists for: the show loads, validates and runs on last week's channel
    map. `--check` is the question, exit 1 is the answer.
    """
    config = toolkit_config_from(Path.cwd())
    fixtures = fixture_dirs(args.fixtures or (), (), None, Path.cwd())
    if fixtures:
        config = replace(config, fixtures=fixtures)
    items = install_plan(config, user_dir=qlc_user_dir(), gobo_dir=qlc_gobo_dir())
    behind = [item for item in items if item.needs_copy]
    if not args.check:
        for item in apply_install(behind):
            print(f"  {item.state:<8} {item.source.name} -> {item.destination}")
        print(f"{len(behind)} file(s) copied, {len(items) - len(behind)} already in sync")
        return 0
    for item in behind:
        print(f"  {item.state:<8} {item.source.name} -> {item.destination}")
    if behind:
        print(
            f"QLC+ is behind the repo on {len(behind)} of {len(items)} file(s); run qlctool install"
        )
        return 1
    print(f"QLC+ has every one of the configured {len(items)} file(s)")
    return 0


def cmd_input_profile(args: argparse.Namespace) -> int:
    """Write the SMC-PAD's QLC+ input profile from the map the show uses."""
    Path(args.out).write_bytes(build_input_profile())
    print(f"Wrote {args.out}")
    return 0


def cmd_decompose(args: argparse.Namespace) -> int:
    decompose_workspace(args.workspace, args.out_dir)
    print(
        f"Decomposed {args.workspace} -> {args.out_dir}/ (skeleton.qxw, functions/, manifest.json)"
    )
    return 0


def cmd_compose(args: argparse.Namespace) -> int:
    compose_workspace(args.src_dir, args.out)
    print(f"Composed {args.src_dir}/ -> {args.out}")
    return finish(Path(args.out), args.validate)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qlctool", description=__doc__)
    parser.add_argument(
        "--fixtures",
        action="append",
        metavar="DIR",
        help="a folder of .qxf definitions; repeat for more (default: qlctool.toml)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add_info_parser(sub)
    add_palette_parser(sub)
    add_matrix_parser(sub)
    add_movement_parser(sub)
    add_patch_parser(sub)
    add_newshow_parser(sub)

    add_probe_parser(sub)
    add_layout_parser(sub)
    add_stage_parser(sub)

    p_mvr = sub.add_parser(
        "mvr",
        help="export the placed rig as an MVR package with a GDTF per definition, "
        "for BlenderDMX or any GDTF visualiser",
    )
    p_mvr.add_argument("workspace")
    p_mvr.add_argument("--out", help="output file (default: <workspace>.mvr next to it)")
    p_mvr.add_argument(
        "--gobos",
        metavar="DIR",
        help="folder holding the gobo images the definitions name "
        "(default: Gobos/ next to the workspace)",
    )
    p_mvr.set_defaults(func=cmd_mvr)

    p_val = sub.add_parser("validate", help="load a workspace in headless QLC+ and report problems")
    p_val.add_argument("workspace")
    p_val.set_defaults(func=cmd_validate)

    add_check_parser(sub)

    p_inst = sub.add_parser(
        "install",
        help="copy the configured fixture definitions, input profiles and gobos "
        "into the installed QLC+; --check only reports what it is missing",
    )
    p_inst.add_argument(
        "--check",
        action="store_true",
        help="report stale or missing copies and exit 1 on any, copy nothing",
    )
    p_inst.set_defaults(func=cmd_install)

    p_prof = sub.add_parser(
        "input-profile",
        help="write the SMC-PAD's QLC+ input profile from the show's own map",
    )
    p_prof.add_argument("out", help="destination .qxi file")
    p_prof.set_defaults(func=cmd_input_profile)

    p_dec = sub.add_parser("decompose", help="split a workspace into a git-diffable fragment tree")
    p_dec.add_argument("workspace")
    p_dec.add_argument("out_dir")
    p_dec.set_defaults(func=cmd_decompose)

    add_deskmap_parser(sub)
    add_pad_palette_parser(sub)
    add_mcp_parser(sub)

    p_com = sub.add_parser("compose", help="rebuild a workspace from a fragment tree")
    p_com.add_argument("src_dir")
    p_com.add_argument("out")
    p_com.add_argument(
        "--validate",
        action="store_true",
        help="load the result in headless QLC+ and fail on any problem it reports",
    )
    p_com.set_defaults(func=cmd_compose)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
