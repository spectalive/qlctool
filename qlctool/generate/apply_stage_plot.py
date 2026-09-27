"""Write a rig's real positions into the workspace, straight from a plot.

The counterpart to the generated band layout: where that one arranges fixtures
by what they can do, this one applies what somebody actually built. Nothing is
computed - the plot's numbers go in as they are, and the fixtures it marks as
not rigged are written with QLC+'s Hidden flag so the 2D and 3D views show the
montage and not the whole patch.
"""

from ..monitor_node import write_monitor
from ..stage_plot import StagePlot
from ..workspace import Workspace


def apply_stage_plot(workspace: Workspace, plot: StagePlot) -> StagePlot:
    """Replace the Monitor node with the plot, and hand the plot back."""
    write_monitor(workspace, plot.stage, plot.point_of_view, plot.items, plot.props)
    return plot
