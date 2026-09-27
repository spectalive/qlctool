"""Validate a fixture definition against QLC+'s own schema.

The `.qxf` in this repository were written by hand, and a definition QLC+ half
rejects fails quietly: the fixture still patches, but a channel, a capability or
a physical figure is silently dropped or clamped. `fixture.xsd` is QLC+'s own
schema, vendored from the project (Apache-2.0, same licence as the rest of it),
so the check is exactly the one upstream applies.

It caught a Weight of 0 - the schema requires a positive number - on a
definition that had looked fine for a year.
"""

from pathlib import Path

from lxml import etree

SCHEMA_PATH = Path(__file__).resolve().parent / "library" / "fixture.xsd"


def definition_errors(path: str | Path) -> list[str]:
    """Schema complaints about one definition, empty when it is clean."""
    schema = etree.XMLSchema(etree.parse(str(SCHEMA_PATH)))
    if schema.validate(etree.parse(str(path))):
        return []
    return [f"line {e.line}: {e.message}" for e in schema.error_log]
