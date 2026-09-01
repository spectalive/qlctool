"""Capability resolution against the real Vibra patch.

These pin the join from patched fixture -> definition -> channel roles on the
actual show, so a wrong channel offset (which would send colour to the wrong
wire on stage) fails here instead of in front of an audience.
"""

from pathlib import Path

import pytest

from qlctool import roles
from qlctool.capability import FixtureCapabilities
from qlctool.fixture import patched_fixtures
from qlctool.library import FixtureLibrary
from qlctool.workspace import Workspace

REPO = Path(__file__).resolve().parents[3]
SHOW = REPO / "QLC+ Setups" / "DeluxeEventos2.qxw"


@pytest.fixture(scope="module")
def library() -> FixtureLibrary:
    return FixtureLibrary.load()


@pytest.fixture(scope="module")
def fixtures():
    return patched_fixtures(Workspace.load(SHOW).root)


def _caps(fixtures, library, model_contains: str) -> FixtureCapabilities:
    fx = next(f for f in fixtures if model_contains in f.model)
    definition = library.get(fx.manufacturer, fx.model)
    assert definition is not None, f"no definition for {fx.manufacturer}/{fx.model}"
    return FixtureCapabilities.resolve(fx, definition)


def test_library_covers_patch(fixtures, library):
    # Every non-Generic patched model must resolve, or scene generation is blind.
    missing = sorted(
        {
            (f.manufacturer, f.model)
            for f in fixtures
            if library.get(f.manufacturer, f.model) is None and f.manufacturer != "Generic"
        }
    )
    assert missing == [], f"definitions missing for {missing}"


def test_cromowash_red_offset(fixtures, library):
    # Advanced 12ch: Pan,PanFine,Tilt,TiltFine,Speed,Red,... -> Red at offset 5.
    caps = _caps(fixtures, library, "CromoWash100")
    assert caps.offsets_for_role(roles.RED) == [5]
    assert caps.offsets_for_role(roles.GREEN) == [6]
    assert caps.offsets_for_role(roles.BLUE) == [7]
    assert caps.offsets_for_role(roles.DIMMER) == [9]


def test_led_bar_has_eight_rgb_segments(fixtures, library):
    # The 24-channel bar is 8 RGB segments: red maps to eight offsets.
    caps = _caps(fixtures, library, "LED Bar 240")
    assert len(caps.offsets_for_role(roles.RED)) == 8
    assert len(caps.offsets_for_role(roles.GREEN)) == 8
    assert len(caps.offsets_for_role(roles.BLUE)) == 8
