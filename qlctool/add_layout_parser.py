"""The `qlctool layout` subcommand's arguments."""

import argparse

from .cmd_layout import cmd_layout


def add_layout_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    p_lay = sub.add_parser(
        "layout",
        help="add Virtual Console buttons for every function that has a folder",
    )
    p_lay.add_argument("workspace")
    p_lay.add_argument("--columns", type=int, default=6, help="buttons per row (default 6)")
    p_lay.add_argument("--out", help="output file (default: <name>-generado.qxw)")
    p_lay.add_argument(
        "--validate", action="store_true", help="load the result in QLC+ and fail on any problem"
    )
    p_lay.set_defaults(func=cmd_layout)
