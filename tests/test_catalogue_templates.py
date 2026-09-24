"""Catalogue templates: a name with a hole in it, the hole the same in every language."""

import pytest

from qlctool.description.reading.read_names import read_names
from qlctool.names.load_catalogue import load_catalogue
from qlctool.names.sections import SECTIONS
from qlctool.names.shipped_languages import shipped_languages
from qlctool.names.shipped_names import shipped_names
from qlctool.names.template_affixes import template_affixes
from qlctool.names.template_fields import template_fields


def test_fields_are_read_in_order():
    assert template_fields("Desk · {caption} ráfaga {seconds} s") == ("caption", "seconds")
    assert template_fields("Rueda Colores") == ()


def test_every_language_has_the_same_fields_for_an_identifier():
    reference = load_catalogue("es")
    for language in shipped_languages():
        catalogue = load_catalogue(language)
        for section in SECTIONS:
            for identifier, text in reference.get(section, {}).items():
                other = catalogue[section][identifier]
                assert sorted(template_fields(other)) == sorted(template_fields(text)), (
                    f"{language} {section}.{identifier}: {other!r} vs {text!r}"
                )


def test_render_fills_the_fields():
    names = shipped_names("es", {"es": {"auto": "AUTO {x}"}})
    assert names.render("auto", x="YA") == "AUTO YA"


def test_affixes_are_the_text_around_the_field():
    names = shipped_names("es", {"es": {"auto": "Ciclo {what}!"}})
    assert template_affixes(names, "auto") == ("Ciclo ", "!")
    with pytest.raises(ValueError, match="not a template"):
        template_affixes(shipped_names("es"), "party_moment")


def test_an_override_must_keep_the_fields():
    assert read_names({"es": {"party_moment": "Fiesta"}}, "show.toml")
    with pytest.raises(ValueError, match="fields"):
        read_names({"es": {"party_moment": "Fiesta {now}"}}, "show.toml")


def test_affixes_of_a_field_at_either_end():
    front = shipped_names("en", {"en": {"auto": "{name} + Pixels"}})
    assert template_affixes(front, "auto") == ("", " + Pixels")
    back = shipped_names("en", {"en": {"auto": "Cycle {what}"}})
    assert template_affixes(back, "auto") == ("Cycle ", "")


def test_escaped_braces_are_not_a_field():
    escaped = shipped_names("es", {"es": {"auto": "Fiesta {{x}}"}})
    with pytest.raises(ValueError, match="not a template"):
        template_affixes(escaped, "auto")
    mixed = shipped_names("es", {"es": {"auto": "{{Ciclo}} {what}!"}})
    assert template_affixes(mixed, "auto") == ("{Ciclo} ", "!")


def test_a_malformed_override_names_where_it_is():
    with pytest.raises(ValueError, match=r"show\.toml: \[names\.es\] party_moment"):
        read_names({"es": {"party_moment": "Fies{ta"}}, "show.toml")
