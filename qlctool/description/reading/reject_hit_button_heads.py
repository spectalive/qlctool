"""An override may reword a hit button, never part its name from the hit it fires."""

from collections.abc import Mapping

from ...desk_policy import split_caption
from ...names.load_catalogue import load_catalogue

BUTTON_PREFIX = "hit_button_"
HIT_PREFIX = "hit_"


def reject_hit_button_heads(overrides: Mapping[str, Mapping[str, str]], where: str) -> None:
    """Raise when a hit button's name, before " · ", is not its `hit_*` caption, ignoring case.

    Ruling B7: the desk finds each burst by the hit button's name, so
    `hit_button_flash = "BANG · Space"` beside the caption "FLASH" built no
    burst for it and failed deep in the generator ("burst duration must be
    positive: bang") without naming the description (final review of Plan B,
    2026-09-25; refused here since 2026-09-26).
    """
    for language, entries in overrides.items():
        catalogue = load_catalogue(language)
        for button, shipped_button in catalogue["console"].items():
            if not button.startswith(BUTTON_PREFIX):
                continue
            hit = HIT_PREFIX + button.removeprefix(BUTTON_PREFIX)
            if hit not in catalogue["captions"] or (button not in entries and hit not in entries):
                continue
            head = split_caption(entries.get(button, shipped_button))[0]
            caption = entries.get(hit, catalogue["captions"][hit])
            if head.casefold() != caption.strip().casefold():
                renamed = button if button in entries else hit
                raise ValueError(
                    f"{where}: [names.{language}] {renamed} = {entries[renamed]!r} parts the hit "
                    f"button's name {head!r} from its hit's caption {caption!r} ({hit}): the "
                    f"name before ' · ' must be the caption, because the desk finds each burst "
                    f"by it; rename {button} and {hit} together"
                )
