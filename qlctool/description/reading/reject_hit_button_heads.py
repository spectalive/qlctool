"""An override may reword a hit button, never part its name from the hit it fires."""

from collections.abc import Mapping

from ...desk_burst_identifier import desk_burst_identifier
from ...names.load_catalogue import load_catalogue
from ...names.shipped_names import shipped_names

BUTTON_PREFIX = "hit_button_"
HIT_PREFIX = "hit_"


def reject_hit_button_heads(overrides: Mapping[str, Mapping[str, str]], where: str) -> None:
    """Raise when the desk would not find a hit button's own hit by the button's name.

    Ruling B7: the desk finds each burst by the hit button's caption
    (`desk_burst_identifier`: glyph and key hint dropped, exactly one match
    among the captions and colours), so `hit_button_flash` renamed to "BANG"
    with its key hint, beside the caption "FLASH", built no burst for it and failed deep in the
    generator ("burst duration must be positive: bang") without naming the
    description (final review of Plan B, 2026-09-25; refused here since
    2026-09-26). The rule asks the desk's own question, so a name that also
    spells a colour is refused and a leading glyph is not (review of D1).
    """
    for language, entries in overrides.items():
        names = shipped_names(language, overrides)
        catalogue = load_catalogue(language)
        for button in catalogue["console"]:
            if not button.startswith(BUTTON_PREFIX):
                continue
            hit = HIT_PREFIX + button.removeprefix(BUTTON_PREFIX)
            if hit not in catalogue["captions"] or (button not in entries and hit not in entries):
                continue
            caption = names.display(button)
            if desk_burst_identifier(caption, names) != hit:
                renamed = button if button in entries else hit
                raise ValueError(
                    f"{where}: [names.{language}] {renamed} = {entries[renamed]!r}: the desk "
                    f"cannot find the hit {hit} ({names.display(hit)!r}) by its button's "
                    f"caption {caption!r}, because the name before the key hint must spell "
                    f"that hit and nothing else, not a colour or another caption; rename "
                    f"{button} and {hit} together"
                )
