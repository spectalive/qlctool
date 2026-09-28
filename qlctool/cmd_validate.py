"""`qlctool validate`: load a workspace in headless QLC+ and report problems."""

import argparse

from .validate_workspace import validate_workspace


def cmd_validate(args: argparse.Namespace) -> int:
    result = validate_workspace(args.workspace)
    if result.ok:
        print(f"{args.workspace}: QLC+ loaded it with no complaints")
        return 0
    print(f"{args.workspace}: QLC+ reported {len(result.errors)} problem(s)")
    for error in result.errors:
        print(f"  {error}")
    return 1
