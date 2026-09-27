"""What an EFX does to each rigged head: direction, phase and mode, per fixture."""

from lxml import etree

from ..xmlutil import find_local, findall_local
from .efx_driven import EFX_PAN_TILT
from .efx_head import EfxHead


def efx_rigged_heads(efx: etree._Element, rigged: set[int]) -> tuple[EfxHead, ...]:
    """The EFX's per-fixture settings for the `rigged` fixtures, sorted."""
    heads: list[EfxHead] = []
    for element in findall_local(efx, "Fixture"):
        identifier = find_local(element, "ID")
        if identifier is None or not (identifier.text or "").strip().isdigit():
            continue
        fixture_id = int(identifier.text or "")
        if fixture_id not in rigged:
            continue
        direction = find_local(element, "Direction")
        offset = find_local(element, "StartOffset")
        mode = find_local(element, "Mode")
        heads.append(
            (
                fixture_id,
                (direction.text or "") if direction is not None else "",
                int(offset.text or 0) if offset is not None else 0,
                int(mode.text) if mode is not None and mode.text else EFX_PAN_TILT,
            )
        )
    return tuple(sorted(heads))
