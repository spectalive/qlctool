"""Command-line entry point for qlctool.

Thin wrapper over the library so the owner can run generators without writing
Python: inspect a workspace, or generate a colour palette + cycle chaser into a
copy. Never overwrites the input - it always writes a new file.
"""

import argparse

from .add_check_parser import add_check_parser
from .add_compose_parser import add_compose_parser
from .add_decompose_parser import add_decompose_parser
from .add_deskmap_parser import add_deskmap_parser
from .add_info_parser import add_info_parser
from .add_input_profile_parser import add_input_profile_parser
from .add_install_parser import add_install_parser
from .add_layout_parser import add_layout_parser
from .add_matrix_parser import add_matrix_parser
from .add_mcp_parser import add_mcp_parser
from .add_movement_parser import add_movement_parser
from .add_mvr_parser import add_mvr_parser
from .add_newshow_parser import add_newshow_parser
from .add_pad_palette_parser import add_pad_palette_parser
from .add_palette_parser import add_palette_parser
from .add_patch_parser import add_patch_parser
from .add_probe_parser import add_probe_parser
from .add_stage_parser import add_stage_parser
from .add_validate_parser import add_validate_parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="qlctool", description=__doc__)
    parser.add_argument(
        "--fixtures",
        action="append",
        metavar="DIR",
        help="a folder of .qxf definitions; repeat for more (default: qlctool.toml)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    add_info_parser(sub)
    add_palette_parser(sub)
    add_matrix_parser(sub)
    add_movement_parser(sub)
    add_patch_parser(sub)
    add_newshow_parser(sub)

    add_probe_parser(sub)
    add_layout_parser(sub)
    add_stage_parser(sub)
    add_mvr_parser(sub)
    add_validate_parser(sub)
    add_check_parser(sub)
    add_install_parser(sub)
    add_input_profile_parser(sub)
    add_decompose_parser(sub)
    add_deskmap_parser(sub)
    add_pad_palette_parser(sub)
    add_mcp_parser(sub)
    add_compose_parser(sub)

    return parser
