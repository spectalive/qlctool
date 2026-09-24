"""Where a show's own files live: fixture definitions, input profiles, gobo images."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ToolkitConfig:
    """Folders, absolute, in priority order; empty where the config says nothing."""

    fixtures: tuple[Path, ...] = ()
    input_profiles: tuple[Path, ...] = ()
    gobos: tuple[Path, ...] = ()
