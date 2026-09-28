"""The default output path for a generator that never overwrites its input."""

from pathlib import Path


def default_out(src: Path) -> Path:
    return src.with_name(f"{src.stem}-generado{src.suffix}")
