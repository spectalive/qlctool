"""Fold the parked positions into the work light, so it is a whole state.

`Blanco Total` stops whatever was running and lights the rig white - and that
is all it used to write: dimmer, shutter, colour. Everything LTP kept its last
value, because nothing in QLC+ remembers what a channel was before a scene
touched it. From `Todo Negro` after a party level, that meant four white beams
projecting Gobo 5 through an inserted, spinning prism, aimed wherever the
figure had left them: a work light with a kaleidoscope in it (cross-audit,
2026-09-02). `Momento Charla` never had the problem because it *is* a
collection: home position, gobo open, prism out, beside its light.

The work light stays one scene - it is a room state in a solo frame, and a
twin scene with a different id is the shape that keeps chasers from pressing
state buttons by proxy - so the park scenes' values are merged into it here.
A channel the work light already states keeps the work light's value.
"""

from collections.abc import Sequence

from lxml import etree

from ..constants import QLC_NS
from ..workspace import Workspace
from ..xmlutil import findall_local, localname


def park_work_light(workspace: Workspace, scene_id: int, source_ids: Sequence[int | None]) -> int:
    """Merge every FixtureVal of `source_ids` into scene `scene_id`; return pairs added."""
    by_id = {
        int(f.attrib["ID"]): f
        for f in workspace.engine
        if localname(f) == "Function" and f.attrib.get("ID")
    }
    target = by_id[scene_id]
    values = {
        int(v.attrib["ID"]): _pairs(v) for v in findall_local(target, "FixtureVal")
    }
    added = 0
    for source_id in source_ids:
        source = by_id.get(source_id) if source_id is not None else None
        if source is None:
            continue
        for value in findall_local(source, "FixtureVal"):
            fixture_id = int(value.attrib["ID"])
            merged = values.setdefault(fixture_id, {})
            for offset, level in _pairs(value).items():
                if offset not in merged:
                    merged[offset] = level
                    added += 1
    for value in findall_local(target, "FixtureVal"):
        target.remove(value)
    for fixture_id in sorted(values):
        element = etree.SubElement(target, f"{{{QLC_NS}}}FixtureVal")
        element.set("ID", str(fixture_id))
        pairs = sorted(values[fixture_id].items())
        if pairs:
            element.text = ",".join(f"{offset},{level}" for offset, level in pairs)
    return added


def _pairs(value: etree._Element) -> dict[int, int]:
    numbers = [int(n) for n in (value.text or "").split(",") if n != ""]
    return dict(zip(numbers[0::2], numbers[1::2], strict=True))
