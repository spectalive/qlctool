"""The `qlctool validate` subcommand's arguments."""

import argparse

from .cmd_validate import cmd_validate


def add_validate_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    p_val = sub.add_parser("validate", help="load a workspace in headless QLC+ and report problems")
    p_val.add_argument("workspace")
    p_val.set_defaults(func=cmd_validate)
