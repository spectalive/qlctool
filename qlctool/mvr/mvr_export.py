"""What `write_mvr` produced: the package, what went in, what stayed out."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class MvrExport:
    path: Path
    fixtures: list[str] = field(default_factory=list)
    gdtf_files: list[str] = field(default_factory=list)
    # "name [id]" -> why it was left out.
    skipped: dict[str, str] = field(default_factory=dict)
