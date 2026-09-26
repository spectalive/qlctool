"""A rig of one fixture model, all in one row group: pars only, washes only.

2026-09-26, round G: `newshow` builds a show for these since movement and the
dimmer chases became optional. `spec` is a `patch --add` line with
`{address}` and `{index}` left to fill.
"""

import shutil
from pathlib import Path

from qlctool.cli import main

EMPTY = Path(__file__).resolve().parent / "data" / "empty-workspace.qxw"


def build_single_shape_patch(folder: Path, spec: str, count: int, width: int) -> Path:
    """Write shape-patch.qxw into `folder`: `count` fixtures `width` channels apart, grouped."""
    empty = folder / "empty.qxw"
    shutil.copy(EMPTY, empty)
    adds = []
    for index in range(1, count + 1):
        adds += ["--add", spec.format(address=1 + (index - 1) * width, index=index)]
    patched = folder / "patched.qxw"
    group = ["--group-new", f"Row={count}x1"]
    assert main(["patch", str(empty), *adds, *group, "--out", str(patched)]) == 0
    cells = [arg for i in range(count) for arg in ("--group-add", f"0={i}@{i},0")]
    out = folder / "shape-patch.qxw"
    assert main(["patch", str(patched), *cells, "--out", str(out)]) == 0
    empty.unlink()
    patched.unlink()
    return out
