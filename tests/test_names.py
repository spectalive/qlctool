"""Names in any shipped language resolve to one stable identifier (2026-09-24, spec step 3)."""

import pytest

from qlctool.names.load_catalogue import load_catalogue
from qlctool.names.name_resolution_error import NameResolutionError
from qlctool.names.names import Names
from qlctool.names.sections import SECTIONS
from qlctool.names.shipped_languages import shipped_languages
from qlctool.names.shipped_names import shipped_names


def test_english_and_spanish_ship():
    assert {"en", "es"} <= set(shipped_languages())


@pytest.mark.parametrize("spelling", ["red", "Red", "rojo", "Rojo", "ROJO", " rojo "])
def test_a_colour_is_the_same_colour_in_any_language(spelling):
    assert shipped_names().identify(spelling, ("colors",)) == "red"


def test_the_show_language_picks_the_display_name():
    assert shipped_names("es").display("party_moment") == "Momento Fiesta"
    assert shipped_names("en").display("party_moment") == "Party Moment"


def test_a_description_overrides_one_display_name():
    names = shipped_names("es", {"es": {"party_moment": "Fiestón"}})
    assert names.display("party_moment") == "Fiestón"
    assert names.identify("fiestón", ("functions",)) == "party_moment"
    assert names.display("calm_moment") == "Momento Tranquilo"


def test_an_unknown_name_lists_the_close_matches():
    with pytest.raises(NameResolutionError, match="Rojo"):
        shipped_names().identify("Roja", ("colors",))


def test_an_ambiguous_name_lists_every_match():
    names = Names(language="xx", catalogues={"xx": {"colors": {"dawn": "Alba", "dusk": "alba"}}})
    with pytest.raises(NameResolutionError, match="dawn, dusk"):
        names.identify("ALBA", ("colors",))


def test_an_unknown_language_is_refused():
    with pytest.raises(NameResolutionError, match="shipped"):
        shipped_names("fr")


@pytest.mark.parametrize("language", ["en", "es"])
def test_every_catalogue_carries_the_same_identifiers(language):
    reference = {section: list(entries) for section, entries in load_catalogue("en").items()}
    assert {s: list(e) for s, e in load_catalogue(language).items()} == reference
    assert tuple(reference) == SECTIONS


def test_an_identifier_lives_in_one_section_only():
    seen = [identifier for entries in load_catalogue("en").values() for identifier in entries]
    assert len(seen) == len(set(seen))


def test_no_shipped_spelling_names_two_identifiers():
    names = shipped_names()
    for section in SECTIONS:
        for identifier in names.identifiers(section):
            for spelling in names.spellings(identifier):
                assert names.lookup(spelling, (section,)) == (identifier,), spelling
