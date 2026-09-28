"""The `qlctool movement` subcommand's arguments."""

import argparse

from .cmd_movement import cmd_movement
from .efx_algorithms import EFX_ALGORITHMS


def add_movement_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    p_mov = sub.add_parser("movement", help="generate movement EFX across every moving head")
    p_mov.add_argument("workspace")
    p_mov.add_argument(
        "--algorithms", help=f"comma-separated EFX algorithms (default: {','.join(EFX_ALGORITHMS)})"
    )
    p_mov.add_argument(
        "--propagation", default="Parallel", choices=["Parallel", "Serial", "Asymmetric"]
    )
    p_mov.add_argument("--out", help="output file (default: <name>-generado.qxw)")
    p_mov.add_argument("--no-chaser", action="store_true", help="EFX only, skip the cycle chaser")
    p_mov.add_argument(
        "--buttons",
        action="store_true",
        help="also add Virtual Console buttons for what was generated",
    )
    p_mov.add_argument(
        "--validate",
        action="store_true",
        help="load the result in headless QLC+ and fail on any problem it reports",
    )
    p_mov.set_defaults(func=cmd_movement)
