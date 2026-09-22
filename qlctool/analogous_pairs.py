"""The two-colour looks that may share a wash: neighbours on the colour wheel.

A split puts odd fixtures on one colour and even on the other, inside one
group - the PARs on the same truss, the bars on the same wall. Where their
pools overlap they mix, and two *complementary* colours mix towards white,
which is the one thing the owner asked to keep out of the rotations. Two
**analogous** colours - neighbours, sixty degrees or less apart - mix to the
hue between them: red beside amber is orange, blue beside magenta is violet,
still a colour. So these are the only pairs the per-group mix wheels step,
plus the show's own blue/red keys (`KEY_SPLIT_PAIRS`), a triad the rule
tolerates (`rule_split_complementary`).

Red over yellow is the owner's example ("rojo/amarillo", 2026-09-22); the rest
walk the wheel: red-magenta, magenta-blue, blue-cyan, cyan-green,
green-yellow, yellow-amber. The lead is the warmer or paler of the two, the
one that dominates (`color_pair`).
"""

from .color_pair import ColorPair

ANALOGOUS_PAIRS: tuple[ColorPair, ...] = (
    ColorPair("Rojo", "Amarillo"),
    ColorPair("Ambar", "Rojo"),
    ColorPair("Rojo", "Magenta"),
    ColorPair("Magenta", "Azul"),
    ColorPair("Cyan", "Azul"),
    ColorPair("Verde", "Cyan"),
    ColorPair("Amarillo", "Verde"),
)
