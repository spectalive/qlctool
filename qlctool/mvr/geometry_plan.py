"""What `build_geometry` made and what the channels need to know about it."""

from dataclasses import dataclass

from pygdtf import Geometry, Model


@dataclass(frozen=True)
class GeometryPlan:
    models: list[Model]
    root: Geometry
    root_name: str
    # One beam geometry per head, in head order: `Beam1`, `Beam2`, ...
    beams: tuple[str, ...]
    # Where a channel outside every head goes.
    emitter: str
    pan: str | None
    tilt: str | None
