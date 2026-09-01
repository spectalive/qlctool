"""One file the repo ships and QLC+ has to be handed a copy of."""

from dataclasses import dataclass
from pathlib import Path

SYNCED = "synced"
STALE = "stale"
MISSING = "missing"


@dataclass(frozen=True)
class InstallItem:
    source: Path
    destination: Path
    state: str

    @property
    def needs_copy(self) -> bool:
        return self.state != SYNCED
