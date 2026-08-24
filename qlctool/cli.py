"""Command-line entry point for qlctool.

Thin wrapper over the library so the owner can run generators without writing
Python: inspect a workspace, or generate a colour palette + cycle chaser into a
copy. Never overwrites the input - it always writes a new file.
"""

import argparse
from pathlib import Path

from .capabilities_of import capabilities_of
from .compose import compose_workspace
from .decompose import decompose_workspace
from .generate.color_palette import generate_color_palette
from .library import FixtureLibrary
from .workspace import Workspace


def _default_out(src: Path) -> Path:
    return src.with_name(f"{src.stem}-generado{src.suffix}")


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
    return 0


def cmd_palette(args: argparse.Namespace) -> int:
    src = Path(args.workspace)
    out = Path(args.out) if args.out else _default_out(src)

    ws = Workspace.load(src)
    library = FixtureLibrary.load()
    result = generate_color_palette(ws, library, make_chaser=not args.no_chaser)
    ws.save(out)

    print(f"Generated {len(result.scene_ids)} colour scenes"
          + ("" if result.chaser_id is None else " + 1 cycle chaser"))
    print(f"Wrote {out}")
    print("Open it in QLC+ to verify before using it in a show.")
    return 0


def cmd_decompose(args: argparse.Namespace) -> int:
    decompose_workspace(args.workspace, args.out_dir)
    print(f"Decomposed {args.workspace} -> {args.out_dir}/ "
          "(skeleton.qxw, functions/, manifest.json)")
    return 0


def cmd_compose(args: argparse.Namespace) -> int:
    compose_workspace(args.src_dir, args.out)
    print(f"Composed {args.src_dir}/ -> {args.out}")
    print("Open it in QLC+ to verify before using it in a show.")
    return 0


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
    p_pal.set_defaults(func=cmd_palette)

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
    p_com.set_defaults(func=cmd_compose)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
