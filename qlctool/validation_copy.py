"""The file validation hands QLC+: an I/O-free copy, beside the original when it can be."""

import tempfile
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from .offline_workspace import offline_workspace


@contextmanager
def validation_copy(path: Path) -> Iterator[Path]:
    """Yield an offline copy of `path`, removed afterwards.

    The copy sits in the original's folder, so audio, video and images the
    workspace names relative to itself still resolve as QLC+ would resolve
    them (`Doc::denormalizeComponentPath`). A folder that cannot be written
    falls back to a temporary one.
    """
    name = f".{path.stem}.qlctool-validate-{uuid.uuid4().hex}.qxw"
    try:
        copy = offline_workspace(path, path.parent / name)
    except OSError:
        with tempfile.TemporaryDirectory(prefix="qlctool-validate-") as folder:
            yield offline_workspace(path, Path(folder) / name)
        return
    try:
        yield copy
    finally:
        copy.unlink(missing_ok=True)
