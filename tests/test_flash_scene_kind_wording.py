"""2026-09-26, review of B10 round 2: the English flash message puts no article on a kind.

"but it is a {kind}" read "it is a nothing", "a EFX", "a RGBMatrix". The kind
is a noun in apposition now; the Spanish entry is the one Vibra always printed.
"""

from qlctool.checks.phrase import Phrase
from qlctool.checks.rendered_value import rendered_value
from qlctool.names.load_catalogue import load_catalogue
from qlctool.names.shipped_names import shipped_names


def _said(language: str, kind: object) -> str:
    phrase = Phrase("flash_scene_not_a_scene", {"button": "B", "kind": kind})
    return str(rendered_value(shipped_names(language), phrase))


def test_2026_09_26_the_english_kind_takes_no_article():
    for kind in ("EFX", "RGBMatrix", "Audio", Phrase("flash_scene_nothing")):
        said = _said("en", kind)
        assert " a EFX" not in said and " a RGBMatrix" not in said and " a Audio" not in said
        assert "it is a nothing" not in said
    assert "but its type is EFX:" in _said("en", "EFX")


def test_the_spanish_flash_message_is_unchanged():
    spanish = load_catalogue("es")["findings"]
    assert spanish["flash_scene_not_a_scene"].startswith(
        "cuelga en modo Flash del boton «{button}», pero es un {kind}:"
    )
    assert spanish["flash_scene_nothing"] == "nada"
