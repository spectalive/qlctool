"""`qlctool compose`: rebuild a workspace from a fragment tree."""

import argparse
from pathlib import Path

from .compose_workspace import compose_workspace
from .finish import finish


def cmd_compose(args: argparse.Namespace) -> int:
    compose_workspace(args.src_dir, args.out)
    print(f"Composed {args.src_dir}/ -> {args.out}")
    return finish(Path(args.out), args.validate)
