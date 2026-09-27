"""Factory for the live console's `master_button` closure: a button for a master function.

Moved verbatim out of `generate_live_console` (2026-09-27 split): the closure
itself is unchanged, only built by a factory that takes the state it closes
over as explicit arguments.
"""

from collections.abc import Callable, Mapping
from typing import Any

from lxml import etree

from ..argb import argb_from_rgb
from ..vc.build_button import FLASH, TOGGLE
from .bind_pad import bind_pad
from .readable_foreground import readable_foreground


def master_button_factory(
    button: Callable[..., etree._Element],
    master: Mapping[str, int],
    keys: Mapping[str, str],
    flash: set[str],
    glyphs: Mapping[str, str],
    pad_colors: Mapping[str, tuple[int, int, int]],
    pad_bindings: Mapping[str, int],
) -> Callable[..., etree._Element | None]:
    """Build the console's `master_button` closure, bound to the button it wraps."""

    def master_button(
        parent: etree._Element,
        name: str,
        caption: str,
        x: int,
        y: int,
        w: int,
        h: int,
        page: int | None = None,
        function_id: int | None = None,
        include_key: bool = True,
        **kwargs: Any,
    ) -> etree._Element | None:
        """A button for a master function, with its key, glyph and action."""
        target_id = function_id if function_id is not None else master.get(name)
        if target_id is None:
            return None
        # The glyph travels in the caption: QLC+'s own <Icon> is a path into the
        # show Mac's disk, and a missing file is a blank button there and
        # nowhere else (`control_glyph`, 2026-09-22).
        mark = glyphs.get(name, "")
        if mark and not caption.startswith(mark):
            caption = f"{mark} {caption}"
        # A pad-bound function wears its palette colour, so the console button
        # and the pad LED read as the same surface.
        colour = pad_colors.get(name)
        if colour is not None and "background" not in kwargs:
            kwargs["background"] = str(argb_from_rgb(colour))
            kwargs.setdefault("foreground", str(argb_from_rgb(readable_foreground(colour))))
        element = button(
            parent,
            target_id,
            caption,
            x,
            y,
            w,
            h,
            page=page,
            key=keys.get(name) if include_key else None,
            action=FLASH if name in flash else TOGGLE,
            # A hit must read over the running state, not merely join it.
            # Override only orders the faders: on an HTP channel the level's
            # higher value still wins the compare, so a MiN Wash strobe on its
            # Intensity-group Dimmer/Strobe channel never showed under a level
            # (`rule_strobe_masked_by_htp`, 2026-09-26). ForceLTP writes past it.
            flash_override=name in flash,
            flash_force_ltp=name in flash,
            **kwargs,
        )
        bind_pad(element, pad_bindings, name)
        return element

    return master_button
