"""The `qlctool mvr` subcommand's arguments."""

import argparse

from .cmd_mvr import cmd_mvr


def add_mvr_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
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
