"""The `qlctool newshow` subcommand's arguments."""

import argparse

from .cmd_newshow import cmd_newshow


def add_newshow_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    p_new = sub.add_parser(
        "newshow",
        help="build a fresh show on an existing patch: strip the functions, "
        "generate palette + matrices + movement + console",
    )
    p_new.add_argument(
        "workspace",
        nargs="?",
        help="the show to take the patch from (default: the description's [rig] workspace)",
    )
    p_new.add_argument(
        "--description",
        metavar="FILE",
        help="a show description (.toml): palette, matrices, timing, console, controllers",
    )
    p_new.add_argument(
        "--out",
        help="output file (default: Vibra.qxw beside the workspace; with --description, "
        "the description's [rig] output, and newshow refuses when neither is given)",
    )
    p_new.add_argument(
        "--plot",
        metavar="FILE",
        help="stage plot to place the rig with, instead of the generated band layout",
    )
    p_new.add_argument("--no-buttons", action="store_true", help="skip the Virtual Console layout")
    p_new.add_argument(
        "--beats",
        action="store_true",
        help="run the chases on the music's beat: Beats tempo "
        "plus the audio input as beat generator (needs an "
        "audio input picked in QLC+, or nothing advances)",
    )
    p_new.add_argument(
        "--bpm-tap",
        action="store_true",
        help="the build for a QLC+ newer than 5.2.2: chases in "
        "Beats tempo and page 1's tap dial driving the "
        "global BPM (ControlBPM), which 5.2.2 ignores",
    )
    p_new.add_argument(
        "--validate", action="store_true", help="load the result in QLC+ and fail on any problem"
    )
    p_new.set_defaults(func=cmd_newshow)
