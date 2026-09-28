"""Split a workspace into a git-diffable fragment tree (approach B).

Every Function becomes its own file under `functions/`; everything else stays in
`skeleton.qxw` in place. `manifest.json` records the exact order of the Engine's
children so `compose` can rebuild a byte-meaningful-identical workspace. This is
what makes the show diffable and lets AI edit one function at a time.
"""

import json
from pathlib import Path

from .function_filename import function_filename
from .localname import localname
from .workspace import Workspace
from .write_fragment import write_fragment

MANIFEST = "manifest.json"
SKELETON = "skeleton.qxw"
FUNCTIONS_DIR = "functions"


def decompose_workspace(src: str | Path, out_dir: str | Path) -> None:
    out = Path(out_dir)
    (out / FUNCTIONS_DIR).mkdir(parents=True, exist_ok=True)

    ws = Workspace.load(src)
    engine = ws.engine

    engine_order: list[dict] = []
    for child in list(engine):
        if localname(child) == "Function":
            filename = function_filename(child)
            write_fragment(out / FUNCTIONS_DIR / filename, child)
            engine_order.append({"function": filename})
            engine.remove(child)
        else:
            engine_order.append({"keep": localname(child)})

    ws.save(out / SKELETON)
    manifest = {"root_tag": localname(ws.root), "engine_order": engine_order}
    (out / MANIFEST).write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
