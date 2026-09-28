"""The `qlctool compose` subcommand's arguments."""

import argparse

from .cmd_compose import cmd_compose


def add_compose_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    p_com = sub.add_parser("compose", help="rebuild a workspace from a fragment tree")
    p_com.add_argument("src_dir")
    p_com.add_argument("out")
    p_com.add_argument(
        "--validate",
        action="store_true",
        help="load the result in headless QLC+ and fail on any problem it reports",
    )
    p_com.set_defaults(func=cmd_compose)
