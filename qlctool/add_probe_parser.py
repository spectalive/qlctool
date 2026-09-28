"""The `qlctool probe` subcommand's arguments."""

import argparse

from .cmd_probe import cmd_probe


def add_probe_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    p_prb = sub.add_parser(
        "probe",
        help="one scene per DMX channel of a fixture, to find out on site what each channel does",
    )
    p_prb.add_argument("workspace")
    p_prb.add_argument("fixture", type=int, help="fixture ID (see `qlctool info`)")
    p_prb.add_argument(
        "--value", type=int, default=255, help="value to drive the channel under test (default 255)"
    )
    p_prb.add_argument(
        "--base",
        metavar="CH=VAL,...",
        help="channels to hold steady while probing, 1-based "
        "(e.g. a dimmer that must be open: 7=255)",
    )
    p_prb.add_argument(
        "--hold", type=int, default=3000, help="ms per step in the walk chaser (default 3000)"
    )
    p_prb.add_argument("--buttons", action="store_true", help="also add Virtual Console buttons")
    p_prb.add_argument("--out", help="output file (default: <name>-generado.qxw)")
    p_prb.add_argument(
        "--validate", action="store_true", help="load the result in QLC+ and fail on any problem"
    )
    p_prb.set_defaults(func=cmd_probe)
