"""Build a QLC+ RGBMatrix <Function> element.

An RGBMatrix runs an algorithm over a fixture group's X/Y grid in one or two
colours. Child order matters to nothing QLC+ reads, but it is written here in
the exact order the production workspaces use, so a generated function is
byte-comparable with a hand-built one.
"""

from lxml import etree

from ..argb import RGB, argb_from_rgb
from ..color_format import INDEXED, LEGACY
from ..constants import ALL_FIXTURES_GROUP, QLC_NS


def build_rgbmatrix(
    function_id: int,
    name: str,
    algorithm: str | None,
    mono_color: RGB,
    group_id: int = ALL_FIXTURES_GROUP,
    end_color: RGB | None = None,
    control_mode: str = "RGB",
    direction: str = "Forward",
    run_order: str = "Loop",
    fade_in: int = 0,
    fade_out: int = 0,
    duration: int = 478,
    properties: dict[str, str] | None = None,
    color_format: str = LEGACY,
    path: str | None = None,
) -> etree._Element:
    """Return a `<Function Type="RGBMatrix">` element.

    algorithm is an RGB script name (see matrix_algorithms.SCRIPT_ALGORITHMS);
    None writes `<Algorithm Type="Plain"/>`, the solid-colour matrix. Colours are
    (r, g, b) and are stored as 32-bit ARGB. group_id is a `<FixtureGroup>` ID,
    or ALL_FIXTURES_GROUP for every fixture. properties are the script's own
    parameters (`blockSize`, `presetIndex`, ...), written in the given order -
    their names and values belong to the script and are not validated here.
    """
    function = etree.Element(f"{{{QLC_NS}}}Function")
    function.set("ID", str(function_id))
    function.set("Type", "RGBMatrix")
    function.set("Name", name)
    if path is not None:
        function.set("Path", path)

    speed = etree.SubElement(function, f"{{{QLC_NS}}}Speed")
    speed.set("FadeIn", str(fade_in))
    speed.set("FadeOut", str(fade_out))
    speed.set("Duration", str(duration))

    etree.SubElement(function, f"{{{QLC_NS}}}Direction").text = direction
    etree.SubElement(function, f"{{{QLC_NS}}}RunOrder").text = run_order

    algo = etree.SubElement(function, f"{{{QLC_NS}}}Algorithm")
    if algorithm is None:
        algo.set("Type", "Plain")
    else:
        algo.set("Type", "Script")
        algo.text = algorithm

    colors = [mono_color] + ([] if end_color is None else [end_color])
    if color_format == INDEXED:
        for index, color in enumerate(colors):
            element = etree.SubElement(function, f"{{{QLC_NS}}}Color")
            element.set("Index", str(index))
            element.text = str(argb_from_rgb(color))
    else:
        mono = etree.SubElement(function, f"{{{QLC_NS}}}MonoColor")
        mono.text = str(argb_from_rgb(mono_color))
        if end_color is not None:
            end = etree.SubElement(function, f"{{{QLC_NS}}}EndColor")
            end.text = str(argb_from_rgb(end_color))

    etree.SubElement(function, f"{{{QLC_NS}}}ControlMode").text = control_mode
    etree.SubElement(function, f"{{{QLC_NS}}}FixtureGroup").text = str(group_id)

    for prop_name, prop_value in (properties or {}).items():
        prop = etree.SubElement(function, f"{{{QLC_NS}}}Property")
        prop.set("Name", prop_name)
        prop.set("Value", str(prop_value))

    return function
