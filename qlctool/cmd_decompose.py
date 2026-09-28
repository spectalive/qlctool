"""`qlctool decompose`: split a workspace into a git-diffable fragment tree."""

import argparse

from .decompose_workspace import decompose_workspace


def cmd_decompose(args: argparse.Namespace) -> int:
    decompose_workspace(args.workspace, args.out_dir)
    print(
        f"Decomposed {args.workspace} -> {args.out_dir}/ (skeleton.qxw, functions/, manifest.json)"
    )
    return 0
