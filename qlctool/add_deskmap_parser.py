"""Register `qlctool deskmap`'s CLI arguments."""

import argparse

from .cmd_deskmap import cmd_deskmap


def add_deskmap_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    parser = sub.add_parser(
        "deskmap",
        help="write the tablet desk's map: pages, controls, swatches and dials from the saved show",
    )
    parser.add_argument("workspace")
    parser.add_argument("--out", required=True, help="the JSON file to write")
    parser.add_argument(
        "--description",
        help="the show description whose language and names the map uses "
        "(default: the language the workspace was generated in)",
    )
    parser.set_defaults(func=cmd_deskmap)
