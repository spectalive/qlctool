"""Catalogue templates: a name with a hole in it, the hole the same in every language."""

from pathlib import Path

import pytest

from qlctool import roles
from qlctool.description.reading.read_names import read_names
from qlctool.fixture_group import fixture_groups
from qlctool.generate.matrix_effects import generate_matrix_effects
from qlctool.generate.movement_families import generate_movement_families
from qlctool.generate.wheel_scenes import generate_wheel_scenes
from qlctool.library import FixtureLibrary
from qlctool.names.load_catalogue import load_catalogue
from qlctool.names.sections import SECTIONS
from qlctool.names.shipped_languages import shipped_languages
from qlctool.names.shipped_names import shipped_names
from qlctool.names.template_affixes import template_affixes
from qlctool.names.template_fields import template_fields
from qlctool.skeleton import strip_to_skeleton
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, findall_local

SETUPS = Path(__file__).resolve().parents[3] / "QLC+ Setups"
SHOW = SETUPS / "DeluxeEventos2.qxw"


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


@pytest.mark.parametrize("language", ["es", "en"])
def test_the_matrix_cycle_starts_with_the_cycle_prefix(language):
    """The console strips the cycle prefix from "Ciclo Matrices <group>" (B8, P12)."""
    names = shipped_names(language)
    workspace = Workspace.load(SHOW)
    group = fixture_groups(workspace.root)[0]
    generated = generate_matrix_effects(
        workspace,
        group_id=group.group_id,
        algorithms=["Fill"],
        palette={"Rojo": (255, 0, 0)},
        names=names,
    )
    engine = find_local(workspace.root, "Engine")
    chaser = next(
        f for f in findall_local(engine, "Function") if f.attrib["ID"] == str(generated.chaser_id)
    )
    prefix, _ = template_affixes(names, "cycle")
    cycle = chaser.attrib["Name"]
    assert cycle.startswith(prefix)
    assert cycle.removeprefix(prefix) == names.render("matrices_of", group=group.name)
    assert chaser.attrib["Path"] == names.display("path_matrices_generated")


@pytest.mark.parametrize("language", ["es", "en"])
def test_a_movement_pick_starts_with_the_movement_prefix(language):
    """play_page strips the movement prefix from pick captions (B8, P12)."""
    names = shipped_names(language)
    workspace = strip_to_skeleton(Workspace.load(SETUPS / "Vibra.qxw"))
    generated = generate_movement_families(workspace, FixtureLibrary.load(), names=names)
    engine = find_local(workspace.root, "Engine")
    by_id = {f.attrib["ID"]: f for f in findall_local(engine, "Function")}
    circle = by_id[str(generated.play_pick_ids[0])]
    prefix, _ = template_affixes(names, "movement_shape")
    assert circle.attrib["Name"].startswith(prefix)
    assert circle.attrib["Name"].removeprefix(prefix) == names.display("shape_circle")
    assert circle.attrib["Path"] == names.display("path_movement")


WHEEL_FOLDERS = {"es": "Gobo (generado)", "en": "Gobo (generated)"}


@pytest.mark.parametrize("language", ["es", "en"])
def test_wheel_animations_are_the_functions_keys_bind(language):
    """The wheel chasers are named exactly what `functions` binds (P12)."""
    names = shipped_names(language)
    workspace = strip_to_skeleton(Workspace.load(SETUPS / "Vibra.qxw"))
    library = FixtureLibrary.load()
    gobo = generate_wheel_scenes(workspace, library, names=names)
    prism = generate_wheel_scenes(
        workspace, library, role=roles.PRISM, label=names.display("prism_label"), names=names
    )
    engine = find_local(workspace.root, "Engine")
    by_id = {f.attrib["ID"]: f for f in findall_local(engine, "Function")}
    gobo_chaser = by_id[str(gobo.chaser_id)]
    assert gobo_chaser.attrib["Name"] == names.display("gobo_animation")
    assert gobo_chaser.attrib["Path"] == WHEEL_FOLDERS[language]
    assert by_id[str(prism.chaser_id)].attrib["Name"] == names.display("prism_animation")


HIT_BUTTONS = {
    "hit_button_flash": "hit_flash",
    "hit_button_flash_slow": "hit_flash_slow",
    "hit_button_flash_colour": "hit_flash_colour",
    "hit_button_smoke_now": "hit_smoke_now",
    "hit_button_vertical_smoke_now": "hit_vertical_smoke_now",
    "hit_button_strobe": "hit_strobe",
    "hit_button_strobe_soft": "hit_strobe_soft",
}


@pytest.mark.parametrize("language", ["es", "en"])
def test_a_hit_button_starts_with_the_caption_the_desk_knows(language):
    """Ruling B7: the key hint rides in the caption; the head is the desk's word."""
    names = shipped_names(language)
    for button, caption in HIT_BUTTONS.items():
        assert names.display(button).split(" · ")[0] == names.display(caption)
