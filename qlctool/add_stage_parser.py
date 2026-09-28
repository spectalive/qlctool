"""The `qlctool stage` subcommand's arguments."""

import argparse

from .cmd_stage import cmd_stage
from .generate.generate_stage_layout import DEFAULT_STAGE
from .prop_item import POINTS_OF_VIEW


def add_stage_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    p_stage = sub.add_parser(
        "stage",
        help="place every fixture in the 2D/3D view: a row per band, spread across the stage",
    )
    p_stage.add_argument("workspace")
    p_stage.add_argument(
        "--plot",
        metavar="FILE",
        help="a written stage plot to apply verbatim; without it the layout is "
        "generated from what each fixture can do",
    )
    p_stage.add_argument(
        "--stage",
        metavar="WxHxD",
        help="stage size in metres (default "
        f"{DEFAULT_STAGE[0]}x{DEFAULT_STAGE[1]}x{DEFAULT_STAGE[2]})",
    )
    p_stage.add_argument(
        "--pov",
        default="front",
        choices=sorted(POINTS_OF_VIEW),
        help="point of view the 2D view opens in (default front)",
    )
    p_stage.add_argument("--out", help="output file (default: <name>-generado.qxw)")
    p_stage.add_argument(
        "--validate", action="store_true", help="load the result in QLC+ and fail on any problem"
    )
    p_stage.set_defaults(func=cmd_stage)
