"""The `[findings]` entry a finding of `rule_caption_promise` names each promise with.

The words themselves ("rueda de gobos", "a gobo wheel") are the catalogue's
(ruling B10, round 2), so an English show's finding names them in English.
"""

from .caption_promises import (
    BAR,
    BEAM_WHEEL,
    BUILTIN_EFFECTS,
    DIMMER,
    GOBO,
    HAZE,
    HEADS,
    PANEL,
    PRISM,
)

PROMISE_WORDS: dict[str, str] = {
    GOBO: "promise_gobo",
    PRISM: "promise_prism",
    HAZE: "promise_haze",
    BEAM_WHEEL: "promise_beam_wheel",
    BAR: "promise_bar",
    PANEL: "promise_panel",
    BUILTIN_EFFECTS: "promise_builtin_effects",
    HEADS: "promise_heads",
    DIMMER: "promise_dimmer",
}
