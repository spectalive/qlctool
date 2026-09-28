"""The `qlctool input-profile` subcommand's arguments."""

import argparse

from .cmd_input_profile import cmd_input_profile


def add_input_profile_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    p_prof = sub.add_parser(
        "input-profile",
        help="write the SMC-PAD's QLC+ input profile from the show's own map",
    )
    p_prof.add_argument("out", help="destination .qxi file")
    p_prof.set_defaults(func=cmd_input_profile)
