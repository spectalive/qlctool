"""The `qlctool info` subcommand's arguments."""

import argparse

from .cmd_info import cmd_info


def add_info_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    p_info = sub.add_parser("info", help="list patched fixtures and their roles")
    p_info.add_argument("workspace")
    p_info.set_defaults(func=cmd_info)
