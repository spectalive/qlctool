"""No Spanish word survives an English build (2026-09-25).

Every catalogue identifier is overridden with a marker that keeps its fields,
so any function name, path or caption that still comes out in Spanish was
written by the generator, not the catalogue.

The patch is the show's own data, not the generator's: a fixture, a fixture
group or a wheel slot may carry a Spanish word, and it is written through
verbatim. Those exemptions are read from the loaded workspace and its
definitions before generation (ruling P17), never from a hand-kept list.
"""

import re
from dataclasses import replace
from pathlib import Path

import pytest

from qlctool.description.controller_settings import ControllerSettings
from qlctool.description.load_show_description import load_show_description
from qlctool.description.show_description import ShowDescription
from qlctool.desk_function_path import DESK_FUNCTION_PATH
from qlctool.generate.canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.names.load_catalogue import load_catalogue
from qlctool.names.template_fields import template_fields
from qlctool.vibra.description import vibra_description
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local, iter_local, localname

SETUPS = Path(__file__).resolve().parents[3] / "QLC+ Setups"
WORD = r"[^\W\d_]{4,}"
# Ruling B6: a word both catalogues spell alike inside a longer value.
B6_WORDS = {"Color"}
# The wheel channels whose slot names are fixture-definition data.
WHEEL_GROUPS = ("Colour", "Gobo")
# Elements whose `Name` the build copies from its input rather than writes:
# ChannelsGroup is patch data kept by the skeleton (its names are the rig's own
# "Rojo Cabezas"); the IO lines and the web server come from the input
# workspace; MeshItem is the stage plot's scenery; Property is an engine key.
COPIED_NAMES = {
    "ChannelsGroup",
    "Universe",
    "Input",
    "Output",
    "Feedback",
    "NetworkServer",
    "MeshItem",
    "Property",
}


# Every shipped way of building Vibra, and a show without the pad (2026-09-25,
# final review of Plan B: the scan covered only plain Vibra).
VARIANTS = ("plain", "beats", "split", "no-pad")


def _variant(name: str) -> tuple[Workspace, ShowDescription]:
    """The input workspace and the description the variant is built from."""
    source = "Vibra-split.qxw" if name == "split" else "Vibra.qxw"
    workspace = Workspace.load(SETUPS / source)
    if name in ("beats", "split"):
        description = load_show_description(SETUPS / f"vibra-{name}.toml", workspace.root)
    else:
        description = vibra_description()
    if name == "no-pad":
        description = replace(description, controllers=ControllerSettings(tablet_desk=True))
    return workspace, description


def _pseudo() -> dict[str, str]:
    """A marker per identifier; a hit button keeps its hit caption as its head (ruling B7).

    The desk times a burst by the identifier its button's head spells, so a
    marker that broke B7 would stop the build before the scan (2026-09-25).
    """
    english = load_catalogue("en")
    pseudo = {
        identifier: f"⟦{identifier}⟧" + "".join(f"{{{f}}}" for f in template_fields(text))
        for entries in english.values()
        for identifier, text in entries.items()
    }
    for identifier in english["console"]:
        if identifier.startswith("hit_button_"):
            head = pseudo[identifier.replace("hit_button_", "hit_", 1)]
            pseudo[identifier] = f"{head} · {pseudo[identifier]}"
    return pseudo


def _spanish_words() -> set[str]:
    spanish, english = load_catalogue("es"), load_catalogue("en")
    words: set[str] = set()
    for section, entries in spanish.items():
        for identifier, text in entries.items():
            if english[section][identifier] != text:
                same = set(re.findall(WORD, english[section][identifier]))
                words |= {w for w in re.findall(WORD, text) if w not in same}
    return words


def _child(element, name: str) -> str:
    found = find_local(element, name)
    return (found.text or "") if found is not None else ""


def _patch_names(workspace: Workspace, library: FixtureLibrary) -> dict[str, set[str]]:
    """The patch's own names, read before the generator touches the workspace."""
    fixtures = [
        f for f in iter_local(workspace.root, "Fixture") if find_local(f, "Model") is not None
    ]
    groups = {_child(g, "Name") for g in iter_local(workspace.root, "FixtureGroup") if g.get("ID")}
    slots: set[str] = set()
    for fixture in fixtures:
        definition = library.get(_child(fixture, "Manufacturer"), _child(fixture, "Model"))
        if definition is None:
            continue
        for channel in definition.channels.values():
            if channel.group in WHEEL_GROUPS:
                slots |= {capability.name for capability in channel.capabilities}
    return {
        "fixtures": {_child(f, "Name") for f in fixtures},
        "groups": groups,
        "wheel slots": slots,
    }


def _written(workspace: Workspace) -> list[str]:
    """Every name, path and caption the build writes; a console label's text is its Caption."""
    written: list[str] = []
    for element in workspace.root.iter():
        if not isinstance(element.tag, str):
            continue
        if localname(element) not in COPIED_NAMES:
            written.append(element.get("Name", ""))
        written += [element.get("Path", ""), element.get("Caption", "")]
    return [text for text in written if text]


def _without(text: str, names: list[str]) -> str:
    """`text` with each whole patch name blanked out, longest first."""
    for name in names:
        text = re.sub(rf"(?<!\w){re.escape(name)}(?!\w)", " ", text)
    return text


@pytest.fixture(scope="module")
def library() -> FixtureLibrary:
    return FixtureLibrary.load()


@pytest.mark.parametrize("variant", VARIANTS)
def test_the_patch_exemptions_are_read_from_the_workspace(variant, library):
    workspace, _ = _variant(variant)
    patch = _patch_names(workspace, library)
    assert all(patch.values()), {kind: len(names) for kind, names in patch.items()}


@pytest.mark.parametrize("variant", VARIANTS)
def test_no_spanish_catalogue_word_is_written(variant, library):
    workspace, described = _variant(variant)
    patch = _patch_names(workspace, library)
    # Whole patch names are exempt, not their words: a fixture called "Humo
    # Vertical 1" must not hide a generator literal "Humo" (ruling P17).
    exempt = sorted({n for names in patch.values() for n in names if n}, key=len, reverse=True)
    description = replace(described, language="en", names={"en": _pseudo()})
    build_canonical_show(workspace, library, description=description)
    # The scan once passed for months while no desk burst was built: a marker
    # broke ruling B7, so the bursts it was meant to read never existed.
    desk = [
        f for f in iter_local(workspace.root, "Function") if f.get("Path") == DESK_FUNCTION_PATH
    ]
    assert desk, "the pseudo-locale build wrote no desk burst, so the scan cannot cover them"
    words = _spanish_words() - B6_WORDS
    texts = [_without(text, exempt) for text in _written(workspace)]
    leaks = sorted({w for text in texts for w in words if re.search(rf"\b{w}\b", text)})
    assert leaks == []
