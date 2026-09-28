"""The `qlctool matrix` subcommand's arguments."""

import argparse

from .cmd_matrix import cmd_matrix


def add_matrix_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    p_mat = sub.add_parser("matrix", help="generate RGBMatrix effects (algorithm x colour)")
    p_mat.add_argument("workspace")
    p_mat.add_argument(
        "--group", default="all", help="fixture group ID to paint, or 'all' (default)"
    )
    p_mat.add_argument(
        "--algorithms",
        help="comma-separated RGB script names, 'solid' for a "
        "plain colour matrix (default: all known scripts)",
    )
    p_mat.add_argument("--out", help="output file (default: <name>-generado.qxw)")
    p_mat.add_argument(
        "--no-chaser", action="store_true", help="matrices only, skip the cycle chaser"
    )
    p_mat.add_argument(
        "--buttons",
        action="store_true",
        help="also add Virtual Console buttons for what was generated",
    )
    p_mat.add_argument(
        "--validate",
        action="store_true",
        help="load the result in headless QLC+ and fail on any problem it reports",
    )
    p_mat.set_defaults(func=cmd_matrix)
