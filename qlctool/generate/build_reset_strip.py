"""The JUGAR page's reset strip: one button per moment or hit, back to a known state."""

from collections.abc import Callable, Mapping

from lxml import etree

from ..names.names import Names
from ..vc.build_button import FLASH, TOGGLE
from .play_page_layout import GAP, HEADER, LEFT, SMALL_BUTTON_HEIGHT, WIDTH

_RESET_NAMES = (
    "auto",
    "talk_moment",
    "calm_moment",
    "party_moment",
    "frenzy_moment",
    "full_white",
    "all_black",
    "flash_full",
    "flash_colour",
    "smoke_on",
    "strobe_fast",
)
# The reset strip's short captions, keyed by function identifier; AUTO keeps
# its own name. Flash, colour flash, haze and strobe reuse the hit captions,
# whose words are the same (ruling B9).
_RESET_CAPTIONS = (
    ("talk_moment", "reset_talk"),
    ("calm_moment", "reset_calm"),
    ("party_moment", "reset_party"),
    ("frenzy_moment", "reset_frenzy"),
    ("full_white", "reset_white"),
    ("all_black", "reset_black"),
    ("flash_full", "hit_flash"),
    ("flash_colour", "hit_flash_colour"),
    ("smoke_on", "haze_word"),
    ("strobe_fast", "hit_strobe"),
)


def build_reset_strip(
    outer: etree._Element,
    button: Callable[..., object],
    frame: Callable[..., etree._Element],
    label: Callable[..., object],
    master: Mapping[str, int],
    flashes: set[str],
    page: int,
    title_font: str,
    small_font: str,
    vocabulary: Names,
) -> None:
    strip = frame(
        outer,
        vocabulary.display("reset_frame"),
        LEFT,
        56,
        WIDTH,
        90,
        page=page,
        font=title_font,
    )
    label(
        strip,
        vocabulary.display("reset_guidance"),
        GAP,
        HEADER,
        420,
        18,
        font=small_font,
    )
    # A function the show lacks (the haze, on a rig without a machine) takes
    # no place in the strip.
    present = [
        (vocabulary.display(i), master[vocabulary.display(i)])
        for i in _RESET_NAMES
        if master.get(vocabulary.display(i)) is not None
    ]
    pitch = (WIDTH - 426 - 2 * GAP) // max(len(present), 1)
    captions = {
        vocabulary.display(function): vocabulary.display(caption)
        for function, caption in _RESET_CAPTIONS
    }
    for index, (name, function_id) in enumerate(present):
        is_flash = name in flashes
        button(
            strip,
            function_id,
            captions.get(name, name),
            426 + GAP + index * pitch,
            44,
            pitch - 4,
            SMALL_BUTTON_HEIGHT,
            action=FLASH if is_flash else TOGGLE,
            flash_override=is_flash,
            flash_force_ltp=is_flash,
            font=small_font,
        )
