"""The description names things by identifier; the build writes them in the show's words.

2026-09-24, spec step 3: localised to Spanish, the Vibra description is today's
show to the byte (tests/test_vibra_byte_identity.py); localised to English only
the names change. Until the generators' own literals come from the catalogue,
the build refuses any vocabulary but the Spanish one (plan ruling R1).
"""

from dataclasses import replace
from pathlib import Path

import pytest

from qlctool.description.localize_description import localize_description
from qlctool.description.matrices_by_group import matrices_by_group
from qlctool.generate.canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.matrix_algorithms import CURATED_MATRICES
from qlctool.names.check_generator_vocabulary import check_generator_vocabulary
from qlctool.names.shipped_names import shipped_names
from qlctool.palette import PALETTE, PRIMARY_COLORS
from qlctool.vibra.description import vibra_description
from qlctool.vibra.flash_functions import FLASH_FUNCTIONS
from qlctool.vibra.keys import KEYS
from qlctool.vibra.timing import VIBRA_TIMING
from qlctool.workspace import Workspace

SHOW = Path(__file__).resolve().parents[3] / "QLC+ Setups" / "Vibra.qxw"


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


def test_the_generator_refuses_a_vocabulary_it_cannot_write_yet():
    check_generator_vocabulary(shipped_names("es"))
    with pytest.raises(ValueError, match="'en'"):
        check_generator_vocabulary(shipped_names("en"))
    with pytest.raises(ValueError, match="party_moment"):
        check_generator_vocabulary(shipped_names("es", {"es": {"party_moment": "Fiestón"}}))


def test_build_refuses_an_english_description():
    workspace = Workspace.load(SHOW)
    with pytest.raises(ValueError, match="Spanish vocabulary"):
        build_canonical_show(
            workspace,
            FixtureLibrary.load(),
            description=replace(vibra_description(), language="en"),
        )
