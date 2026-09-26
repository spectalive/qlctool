"""The `qlctool check` subcommand's arguments."""

import argparse

from .cmd_check import cmd_check


def add_check_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    parser = sub.add_parser(
        "check",
        help="check what the show will actually do: fixtures coloured but "
        "never lit, colour a fixture can only take on a wheel, two "
        "programmes writing the same channel, and the console's own traps",
    )
    parser.add_argument("workspace")
    parser.add_argument(
        "--limit", type=int, default=20, help="findings printed per rule (default 20)"
    )
    parser.add_argument(
        "--description",
        help="the show description whose language and names the findings use "
        "(default: the language the workspace was generated in)",
    )
    parser.set_defaults(func=cmd_check)
