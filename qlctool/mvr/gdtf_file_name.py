"""The file name a definition's GDTF goes by, inside the MVR and on disk.

GDTF's own convention is `Manufacturer@Model@Revision.gdtf`, and BlenderDMX
looks the fixture up in the package by exactly the string the MVR names. Every
character that a zip entry or a filesystem could object to becomes an
underscore, so `Pro-Lights` and `CromoWash100` survive but `LED Bar 240/8 RGB`
does not turn into a directory.
"""

import re

from ..definition import FixtureDefinition

_UNSAFE = re.compile(r"[^A-Za-z0-9._-]+")


def gdtf_file_name(definition: FixtureDefinition) -> str:
    manufacturer = _UNSAFE.sub("_", definition.manufacturer).strip("_") or "Unknown"
    model = _UNSAFE.sub("_", definition.model).strip("_") or "Unknown"
    return f"{manufacturer}@{model}@qlctool.gdtf"
