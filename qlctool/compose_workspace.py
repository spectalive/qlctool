"""Rebuild a workspace from a decomposed fragment tree (approach B).

Reverses `decompose`: load the skeleton, then rebuild the Engine's children in
the exact order the manifest recorded - non-Function children from the skeleton,
Function children from their fragment files - and save. decompose -> compose is
verified to round-trip semantically, so the fragment tree is a lossless,
diffable representation of the show.
"""

import json
from pathlib import Path

from lxml import etree

from .decompose import FUNCTIONS_DIR, MANIFEST, SKELETON
from .workspace import Workspace
from .xmlutil import localname


def compose_workspace(src_dir: str | Path, out: str | Path) -> None:
    src = Path(src_dir)
    manifest = json.loads((src / MANIFEST).read_text(encoding="utf-8"))

    ws = Workspace.load(src / SKELETON)
    engine = ws.engine

    # The skeleton's Engine holds only the non-Function children, in order.
    kept = [child for child in engine if localname(child) == "Function"]
    assert not kept, "skeleton must not contain Function elements"
    kept_children = list(engine)
    kept_iter = iter(kept_children)

    for child in kept_children:
        engine.remove(child)

    for entry in manifest["engine_order"]:
        if "function" in entry:
            fragment = etree.parse(str(src / FUNCTIONS_DIR / entry["function"]))
            engine.append(fragment.getroot())
        else:
            engine.append(next(kept_iter))

    ws.save(out)
