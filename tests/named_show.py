"""Load one of the rig's shipped shows by file name."""

from rig_root import RIG_ROOT

from qlctool.workspace import Workspace

REPO = RIG_ROOT


def named_show(name="Vibra-split.qxw"):
    return Workspace.load(REPO / "QLC+ Setups" / name)
