"""`qlctool check`: say what the room will do, which is not what QLC+ loading it says."""

import argparse
from pathlib import Path

from .checks.check_workspace import check_workspace
from .description.description_names import description_names
from .description.load_show_description import load_show_description
from .library_for import library_for
from .print_check_report import print_check_report
from .warn_unresolved import warn_unresolved
from .workspace import Workspace


def cmd_check(args: argparse.Namespace) -> int:
    """Say what the room will do, which is not what QLC+ loading it says."""
    workspace = Workspace.load(args.workspace)
    library = library_for(args.fixtures, Path(args.workspace))
    warn_unresolved(workspace.root, library)
    names = None
    if args.description:
        names = description_names(load_show_description(args.description, workspace.root))
    findings = check_workspace(workspace, library, names=names)
    return print_check_report(args.workspace, workspace.root, findings, args.limit, names)
