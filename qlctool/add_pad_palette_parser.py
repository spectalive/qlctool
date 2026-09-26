"""The `qlctool pad-palette` subcommand's arguments."""

import argparse

from .cmd_pad_palette import cmd_pad_palette


def add_pad_palette_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    parser = sub.add_parser(
        "pad-palette",
        help="write the SMC-PAD LED bridge's palette: each pad's note and colours from the saved show",
    )
    parser.add_argument("workspace")
    parser.add_argument("--out", required=True, help="the JSON file to write")
    parser.set_defaults(func=cmd_pad_palette)
