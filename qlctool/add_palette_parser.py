"""The `qlctool palette` subcommand's arguments."""

import argparse

from .cmd_palette import cmd_palette


def add_palette_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    p_pal = sub.add_parser("palette", help="generate colour scenes + cycle chaser")
    p_pal.add_argument("workspace")
    p_pal.add_argument("--out", help="output file (default: <name>-generado.qxw)")
    p_pal.add_argument(
        "--no-chaser", action="store_true", help="scenes only, skip the cycle chaser"
    )
    p_pal.add_argument(
        "--buttons",
        action="store_true",
        help="also add Virtual Console buttons for what was generated",
    )
    p_pal.add_argument(
        "--validate",
        action="store_true",
        help="load the result in headless QLC+ and fail on any problem it reports",
    )
    p_pal.set_defaults(func=cmd_palette)
