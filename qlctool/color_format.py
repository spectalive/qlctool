"""Which shape a workspace uses for RGBMatrix colours.

QLC+ 4.13 wrote `<MonoColor>` plus an optional `<EndColor>`. QLC+ 4.14 replaced
both with an indexed list - `<Color Index="0">`, `<Color Index="1">` - and 5.x
kept it. QLC+ still reads the old shape, but a generator writing into a show
should write the shape that show uses, so a file stays internally consistent.
"""

from lxml import etree

from .xmlutil import find_local, iter_local, localname

LEGACY = "legacy"  # <MonoColor> / <EndColor>
INDEXED = "indexed"  # <Color Index="n">


def color_format_of(root: etree._Element) -> str:
    """Detect the colour shape from the workspace's own RGBMatrix functions.

    Falls back to the Creator version when the show has no matrix yet: 4.14 is
    where the shape changed.
    """
    for function in iter_local(root, "Function"):
        if function.attrib.get("Type") != "RGBMatrix":
            continue
        for child in function:
            if localname(child) == "Color":
                return INDEXED
            if localname(child) in ("MonoColor", "EndColor"):
                return LEGACY

    creator = find_local(root, "Creator")
    version = find_local(creator, "Version") if creator is not None else None
    text = (version.text or "").strip() if version is not None else ""
    try:
        major, minor = (int(part) for part in text.split(".")[:2])
    except ValueError:
        return LEGACY
    return INDEXED if (major, minor) >= (4, 14) else LEGACY
