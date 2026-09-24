"""Where a description's patch, stage plot and output live."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RigFiles:
    """Paths resolved against the description's folder; None where it does not say.

    `output` None means the workspace itself, regenerated in place.
    `fixtures` are the rig's definition folders; empty means found by
    configuration (`fixture_dirs`).
    """

    workspace: Path | None = None
    output: Path | None = None
    stage_plot: Path | None = None
    fixtures: tuple[Path, ...] = ()
