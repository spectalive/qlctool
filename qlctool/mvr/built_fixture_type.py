"""What `build_fixture_type` made: the type, and the images to pack with it."""

from dataclasses import dataclass

import pygdtf


@dataclass(frozen=True)
class BuiltFixtureType:
    fixture_type: pygdtf.FixtureType
    # (path on disk, name inside the archive): the gobo images.
    media: list[tuple[str, str]]
