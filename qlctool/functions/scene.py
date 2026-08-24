"""Build a QLC+ Scene <Function> element.

A Scene holds one <FixtureVal> per fixture, each a flat comma-separated list of
offset,value pairs. This builder writes exactly that, in the QLC+ namespace so
it serializes without a prefix and loads back into QLC+ unchanged.
"""

from lxml import etree

from ..constants import QLC_NS

FixtureValues = dict[int, list[tuple[int, int]]]


def build_scene(
    function_id: int,
    name: str,
    fixture_values: FixtureValues,
    path: str | None = None,
    fade_in: int = 0,
    fade_out: int = 0,
    duration: int = 0,
) -> etree._Element:
    """Return a `<Function Type="Scene">` element.

    fixture_values maps a fixture ID to (offset, value) pairs; offsets are
    0-based within the fixture and values are 0-255. A fixture mapped to an empty
    list is written as a self-closing <FixtureVal> - included, no values set.
    """
    function = etree.Element(f"{{{QLC_NS}}}Function")
    function.set("ID", str(function_id))
    function.set("Type", "Scene")
    function.set("Name", name)
    if path is not None:
        function.set("Path", path)

    speed = etree.SubElement(function, f"{{{QLC_NS}}}Speed")
    speed.set("FadeIn", str(fade_in))
    speed.set("FadeOut", str(fade_out))
    speed.set("Duration", str(duration))

    for fixture_id, pairs in fixture_values.items():
        val = etree.SubElement(function, f"{{{QLC_NS}}}FixtureVal")
        val.set("ID", str(fixture_id))
        if pairs:
            val.text = _encode(pairs)

    return function


def _encode(pairs: list[tuple[int, int]]) -> str:
    ordered = sorted(pairs, key=lambda pair: pair[0])
    return ",".join(f"{offset},{value}" for offset, value in ordered)
