"""Every fixture definition this repository ships has to satisfy QLC+'s schema.

These were written by hand from seller charts, and QLC+ does not refuse a
definition it dislikes - it drops the parts it cannot read and carries on, which
is how a Weight of 0 survived unnoticed.
"""

from pathlib import Path

import pytest

from qlctool.definition_schema import SCHEMA_PATH, definition_errors
from qlctool.library import REPO_FIXTURES, SYSTEM_FIXTURES

DEFINITIONS = sorted(REPO_FIXTURES.glob("*.qxf")) + sorted(SYSTEM_FIXTURES.glob("*.qxf"))


def test_the_schema_is_vendored():
    assert SCHEMA_PATH.is_file()


def test_there_are_definitions_to_check():
    assert len(DEFINITIONS) >= 7


@pytest.mark.parametrize("definition", DEFINITIONS, ids=lambda p: p.stem)
def test_definition_matches_the_qlcplus_schema(definition: Path):
    errors = definition_errors(definition)
    assert not errors, f"{definition.name}:\n  " + "\n  ".join(errors)
