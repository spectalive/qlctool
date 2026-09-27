"""One fixture's spot on the plot, in millimetres."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MonitorItem:
    """One fixture's spot on the plot, in millimetres.

    `hidden` is QLC+'s own flag for a fixture that is patched but not drawn -
    a spare that stays in the workspace without cluttering the views.
    """

    fixture_id: int
    x: float
    y: float
    z: float
    hidden: bool = False
    # Degrees about each axis. A fixture standing on the floor and aimed at the
    # ceiling is x_rot=180: QLC+'s meshes all point down by default, because
    # that is how a light hangs.
    x_rot: float = 0.0
    y_rot: float = 0.0
    z_rot: float = 0.0
