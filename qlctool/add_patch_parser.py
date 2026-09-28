"""The `qlctool patch` subcommand's arguments."""

import argparse

from .cmd_patch import cmd_patch


def add_patch_parser(sub: "argparse._SubParsersAction[argparse.ArgumentParser]") -> None:
    p_patch = sub.add_parser(
        "patch",
        help="check the patch for address overlaps, or edit it (add/re-address/rename/remove)",
    )
    p_patch.add_argument("workspace")
    p_patch.add_argument(
        "--add",
        action="append",
        metavar="SPEC",
        help="Manufacturer|Model|Mode|universe|address[|name], address 1-based",
    )
    p_patch.add_argument(
        "--set-address",
        action="append",
        metavar="ID=U:A",
        help="move fixture ID to universe U, address A (1-based)",
    )
    p_patch.add_argument("--rename", action="append", metavar="ID=NAME")
    p_patch.add_argument(
        "--remove",
        action="append",
        type=int,
        metavar="ID",
        help="unpatch fixture ID and clear every reference",
    )
    p_patch.add_argument(
        "--group-new",
        action="append",
        metavar="NAME=WxH",
        help="create an empty fixture group - two kinds of light in one group share one picture",
    )
    p_patch.add_argument(
        "--group-reshape",
        action="append",
        metavar="GROUP=WxH",
        help="re-place every head in reading order into a "
        "grid with no holes; refuses a size that is not "
        "exactly the group's own",
    )
    p_patch.add_argument(
        "--group-size",
        action="append",
        metavar="GROUP=WxH",
        help="resize a fixture group's grid; refuses a size "
        "that would leave its own heads unreachable",
    )
    p_patch.add_argument(
        "--group-add",
        action="append",
        metavar="GROUP=FIXTURE[:HEAD]@X,Y",
        help="put a fixture's head in a group cell - without "
        "it a fixture gets no colour bank and no matrix. "
        "HEAD defaults to 0; name it for a bar, a panel "
        "or a wash whose rings are all one fixture",
    )
    p_patch.add_argument(
        "--group-sort",
        action="append",
        metavar="GROUP",
        help="re-lay the group's cells in the order the "
        "fixtures stand in the room, so a sweep across "
        "the grid sweeps the stage",
    )
    p_patch.add_argument(
        "--group-move",
        action="append",
        metavar="GROUP=FIXTURE[:HEAD]@X,Y",
        help="move a head already in the group to another "
        "cell; the target cell must be free. HEAD "
        "defaults to 0 - name it for a bar or a panel, "
        "whose heads are all one fixture",
    )
    p_patch.add_argument(
        "--group-remove",
        action="append",
        metavar="GROUP=FIXTURE",
        help="take a fixture out of a group - it then gets no "
        "colour bank and no matrix from that group, and "
        "the cells it held stay empty",
    )
    p_patch.add_argument("--out", help="output file (default: <name>-generado.qxw)")
    p_patch.add_argument(
        "--validate",
        action="store_true",
        help="load the result in headless QLC+ and fail on any problem it reports",
    )
    p_patch.set_defaults(func=cmd_patch)
