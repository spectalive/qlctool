"""The `qlctool decompose` subcommand's arguments."""

import argparse

from .cmd_decompose import cmd_decompose


def add_decompose_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    p_dec = sub.add_parser("decompose", help="split a workspace into a git-diffable fragment tree")
    p_dec.add_argument("workspace")
    p_dec.add_argument("out_dir")
    p_dec.set_defaults(func=cmd_decompose)
