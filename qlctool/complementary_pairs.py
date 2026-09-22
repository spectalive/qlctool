"""The two-colour looks that go *between* roles: heads on one, everything else on the other.

"Tiene que haber alguna regla o recomendaciones sobre eso, cuales casan mejor o
usan los prods" (owner, 2026-09-22). There is, and it is the same in every
source the design note collects (`brain/topics/stage-lighting-design`, HARMAN
above all): the strong two-colour look is **complementary** - hues opposite
each other - and complementary colours **on the same surface desaturate each
other towards white**, so the contrast is placed between roles, heads against
the wash, never inside one wash. These are those pairs, and they are used for
exactly that: `Cabezas <lead> / Resto <bed>`.

The lead is the warm colour, because warm dominates cool: the heads carry
the colour the eye ranks first and the bed sits under them. Amber over blue is
the classic stage pairing (the tungsten-and-sky look every LD starts from);
yellow over blue is the owner's own example ("amarillo/azul"); red over cyan
and magenta over green are the other two opposites the palette has. Blue over
red is not complementary - a triad, 120 degrees - but it is the hand-built
show's own key-9 look and the one contrast the owner has been pressing for
years, so it stays.
"""

from .color_pair import ColorPair

COMPLEMENTARY_PAIRS: tuple[ColorPair, ...] = (
    ColorPair("Ambar", "Azul"),
    ColorPair("Amarillo", "Azul"),
    ColorPair("Rojo", "Cyan"),
    ColorPair("Magenta", "Verde"),
    ColorPair("Rojo", "Azul"),
)
