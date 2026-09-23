"""Write one definition's GDTF archive to a folder."""

from pathlib import Path

from pygdtf import FixtureTypeWriter

from ..definition import FixtureDefinition
from .build_fixture_type import build_fixture_type
from .gdtf_file_name import gdtf_file_name


def write_gdtf(definition: FixtureDefinition, out_dir: Path, gobo_dir: Path | None) -> Path:
    """The archive's path; `out_dir` is created if missing."""
    built = build_fixture_type(definition, gobo_dir)
    writer = FixtureTypeWriter(built.fixture_type)
    for path, arcname in built.media:
        writer.add_file(path, arcname)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / gdtf_file_name(definition)
    writer.write_gdtf(target)
    return target
