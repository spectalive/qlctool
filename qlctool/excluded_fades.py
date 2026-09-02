"""Read back which channels each fixture tells QLC+ not to fade.

The check side of `exclude_fade`: fixture id -> the offsets listed in that
fixture's `<ExcludeFade>`, empty for a fixture that carries none. A scene may
fade a wheel only if the wheel is in here.
"""

from lxml import etree

from .xmlutil import find_local, findall_local


def excluded_fades(root: etree._Element) -> dict[int, set[int]]:
    engine = find_local(root, "Engine")
    if engine is None:
        return {}
    found: dict[int, set[int]] = {}
    # Direct children only: an EFX carries <Fixture> blocks of its own.
    for fixture in findall_local(engine, "Fixture"):
        identifier = find_local(fixture, "ID")
        if identifier is None or not (identifier.text or "").strip().isdigit():
            continue
        element = find_local(fixture, "ExcludeFade")
        text = (element.text or "") if element is not None else ""
        found[int(identifier.text)] = {
            int(part) for part in text.split(",") if part.strip().isdigit()
        }
    return found
