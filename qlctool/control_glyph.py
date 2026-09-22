"""One glyph per control, so a button says what it does before it is read.

"Ni un solo icono en los botones" (owner, 2026-09-22), looking at a console of
593 buttons whose only non-text mark was the flash hits' colour. QLC+ can carry
a real icon per button - `<Icon>` is a file path - but a path is a promise about
the show Mac's disk, and a missing file is a silently blank button on the one
machine that matters. A glyph travels inside the caption: it survives the
workspace, the tablet desk reading the same map, and a fresh install.

The map is by control, not by kind, because that is what a person recognises: a
haze rhythm and a haze burst are the same cloud, and the four room states are
four different rooms. Anything not named here keeps a plain caption - a glyph
nobody can decode is worse than none.
"""

GLYPHS: dict[str, str] = {
    # The room states.
    "AUTO": "▶",
    "Momento Charla": "🎤",
    "Momento Tranquilo": "🌙",
    "Momento Fiesta": "🎉",
    "Momento Locura": "🔥",
    "Blanco Total": "💡",
    "Todo Negro": "⏹",
    # The hits.
    "Flash 100%": "⚡",
    "Flash 50%": "⚡",
    "Flash Color": "🎨",
    "Humo ON": "☁",
    "Humo Vertical YA": "⇧",
    "Humo Vertical": "⇧",
    "Strobo Rapido": "✳",
    "Strobo Medio": "✳",
    # The haze rhythms, all one family.
    "Humo Auto": "☁",
    "Humo Auto 2 min": "☁",
    "Humo Auto 4 min": "☁",
    "Humo Auto 8 min": "☁",
    # The layers of the JUGAR page.
    "Rueda Colores": "🎨",
    "Rueda Simples": "🎨",
    "Rueda Pastel": "🎨",
    "Rueda Mezcla": "🎨",
    "Luz Charla": "🎤",
    "Movimientos Cabezas": "↔",
    "Movimientos Suaves": "↔",
    "Movimientos Rapidos": "↔",
    "Cabezas Centro": "◎",
    "Gobo Animacion": "❋",
    "Prisma Animacion": "✧",
    "Arcoiris Simultaneo": "🌈",
    "Arcoiris Pasos": "🌈",
    "Dimmer Chase": "◐",
    "Dimmer Chase 2": "◑",
    "Dimmer Secuencia": "◒",
    "Dimmer PingPong": "◓",
    "Strobo ON": "✳",
    "Strobo OFF": "✳",
}


def glyph(name: str) -> str:
    """The glyph for this control, or an empty string when it has none."""
    return GLYPHS.get(name, "")
