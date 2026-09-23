"""One wheel slot: a colour from its hex, or a gobo with its image packed."""

from pathlib import Path

from pygdtf import Resource, WheelSlot

from .cie_from_hex import cie_from_hex
from .find_gobo_image import find_gobo_image
from .gdtf_name import gdtf_name
from .wheel_plan import WheelPlan


def wheel_slot(
    prefix: str, name: str, resource: str, gobo_dir: Path | None, plan: WheelPlan
) -> WheelSlot:
    name = gdtf_name(name)
    if prefix == "Color":
        return WheelSlot(name=name, color=cie_from_hex(resource))
    image = find_gobo_image(resource, gobo_dir)
    if image is None:
        return WheelSlot(name=name)
    arcname = f"wheels/{image.name}"
    if all(existing != arcname for _, existing in plan.media):
        plan.media.append((str(image), arcname))
    return WheelSlot(
        name=name, media_file_name=Resource(image.stem, extension=image.suffix.lstrip("."))
    )
