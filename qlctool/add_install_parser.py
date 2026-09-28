"""The `qlctool install` subcommand's arguments."""

import argparse

from .cmd_install import cmd_install


def add_install_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
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
