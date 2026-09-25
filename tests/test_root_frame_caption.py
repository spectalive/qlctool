"""2026-09-25, the owner's delegated decision: the root console frame is captioned from the catalogue.

`strip_to_skeleton` kept the input workspace's root frame caption, so Vibra
described in English still opened on "Página 1", the caption QLC+ saved in the
Spanish file. The root frame is now captioned in the show's language
(`root_frame`): Spanish keeps "Página 1", so Vibra's bytes stay.
"""

from dataclasses import replace

import pytest
from rig_root import RIG_ROOT

from qlctool.generate.canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.names.shipped_names import shipped_names
from qlctool.vibra.vibra_description import vibra_description
from qlctool.workspace import Workspace
from qlctool.xmlutil import find_local

VIBRA = RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"
# A file whose root frame QLC+ saved with no caption at all.
UNCAPTIONED = RIG_ROOT / "QLC+ Setups" / "DeluxeEventos2.qxw"


def _build(source, language: str, names: dict | None = None) -> Workspace:
    workspace = Workspace.load(source)
    description = replace(vibra_description(), language=language, names=names or {})
    build_canonical_show(workspace, FixtureLibrary.load(), description=description)
    return workspace


def _root_caption(workspace: Workspace) -> str:
    return find_local(find_local(workspace.root, "VirtualConsole"), "Frame").get("Caption", "")


@pytest.mark.parametrize("language", ["en", "es"])
def test_2026_09_25_the_root_frame_speaks_the_show_language(language):
    workspace = _build(VIBRA, language)
    assert _root_caption(workspace) == shipped_names(language).display("root_frame")
    if language == "en":
        captions = {e.get("Caption") for e in workspace.root.iter() if isinstance(e.tag, str)}
        assert "Página 1" not in captions


def test_2026_09_25_an_uncaptioned_root_frame_is_captioned_too():
    workspace = Workspace.load(UNCAPTIONED)
    assert _root_caption(workspace) == ""
    assert _root_caption(_build(UNCAPTIONED, "en")) == "Page 1"


def test_2026_09_25_the_pseudo_locale_reaches_the_root_frame():
    """The scan in `test_pseudo_locale.py` sees the caption only through its identifier."""
    marker = "⟦root_frame⟧"
    workspace = _build(VIBRA, "en", {"en": {"root_frame": marker}})
    assert _root_caption(workspace) == marker
