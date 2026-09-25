"""The description names things by identifier; the build writes them in the show's words.

2026-09-24, spec step 3: localised to Spanish, the Vibra description is today's
show to the byte (tests/test_vibra_byte_identity.py); localised to English only
the names change. Since Plan B (2026-09-25) the generators' own literals come
from the catalogue too, so any shipped language builds.
"""

from dataclasses import replace

from rig_root import RIG_ROOT

from qlctool.description.localize_description import localize_description
from qlctool.description.matrices_by_group import matrices_by_group
from qlctool.generate.canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.matrix_algorithms import CURATED_MATRICES
from qlctool.names.shipped_names import shipped_names
from qlctool.palette import PALETTE, PRIMARY_COLORS
from qlctool.vibra.flash_functions import FLASH_FUNCTIONS
from qlctool.vibra.keys import KEYS
from qlctool.vibra.timing import VIBRA_TIMING
from qlctool.vibra.vibra_description import vibra_description
from qlctool.workspace import Workspace

SHOW = RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"


def test_the_vibra_description_names_things_by_identifier():
    show = vibra_description()
    assert list(show.colours.palette)[:3] == ["red", "fire_red", "orange"]
    assert show.colours.white == "white"
    assert show.console.keys["auto"] == "Q" and show.console.keys["talk_moment"] == "F1"
    assert "stage_aim" in show.console.flash_functions
    assert show.timing.beat_timings["colour_wheel"].hold == 8
    assert show.matrices["BarrasLed"][0].colors == ("red", "blue")
    assert show.language == "es" and show.names == {}


def test_localised_to_spanish_it_is_todays_show():
    show = localize_description(vibra_description(), shipped_names("es"))
    assert list(show.colours.palette.items()) == list(PALETTE.items())
    assert show.colours.primary == PRIMARY_COLORS
    assert list(show.console.keys.items()) == list(KEYS.items())
    assert show.console.flash_functions == FLASH_FUNCTIONS
    assert list(show.timing.beat_timings.items()) == list(VIBRA_TIMING.beat_timings.items())
    assert show.matrices == matrices_by_group(CURATED_MATRICES)


def test_localised_to_english_only_the_names_change():
    show = localize_description(vibra_description(), shipped_names("en"))
    assert show.colours.palette["Red"] == (255, 0, 0)
    assert show.console.keys["Party Moment"] == "F3"


def test_an_english_description_builds_in_english():
    workspace = Workspace.load(SHOW)
    show = build_canonical_show(
        workspace,
        FixtureLibrary.load(),
        description=replace(vibra_description(), language="en"),
    )
    assert "Party Moment" in show.master_ids
