"""The Vibra console's keyboard: one key per function, as the owner's hands know it."""

# The console the owner works with: one key each. The night-running looks keep
# the letters the hand-built show had, so muscle memory carries over; the
# moments - the states somebody takes the room into by hand - are on F1-F4,
# which is a row of its own and cannot collide with a colour bank on 1-0.
KEYS = {
    # Page 1: the state the room is in, and the hits that ride on top of it.
    "AUTO": "Q",
    "Momento Charla": "F1",
    "Momento Tranquilo": "F2",
    "Momento Fiesta": "F3",
    "Momento Locura": "F4",
    "Blanco Total": "X",
    "Todo Negro": "º",
    "Flash 100%": "Space",
    "Flash 50%": "-",
    "Flash Color": ".",
    "Humo ON": "H",
    "Humo Vertical YA": "U",
    "Strobo Rapido": "F",
    "Strobo Medio": "T",
    # JUGAR hooks retain the hand-built show's global shortcuts; picks and
    # duplicate reset-strip controls remain keyless.
    "Rueda Colores": "W",
    # The other two automatic colour modes (2026-09-22). C is free again since
    # the beams' own wheel walk lost its button.
    "Rueda Simples": "C",
    "Rueda Pastel": "L",
    # The wild looks, on a wheel of their own since 2026-09-22 ("un modo
    # multicolor solo por si acaso", owner). R was free.
    "Rueda Multicolor": "R",
    "Rueda Mezcla": "E",
    "Movimientos Cabezas": "A",
    "Gobo Animacion": "G",
    "Prisma Animacion": "P",
    "Arcoiris Simultaneo": "'",
    "Arcoiris Pasos": "¡",
    "Humo Auto": "J",
    "Humo Vertical": "N",
    # Live-only looks. The hand-built console has these on V/B/C/Z; C is
    # already Color Beam here, so the sequence moves rather than clashes.
    # M is NOT in this family: it was the hand-built console's tap-tempo key
    # on every speed dial, and the owner's tapping hand remembers it - so the
    # sequence sits on K and M goes back to the colour dial's tap
    # (2026-08-29, "ajustar la velocidad con tap ... es algo que usamos
    # bastante").
    "Dimmer Chase": "V",
    "Dimmer Chase 2": "B",
    "Dimmer Secuencia": "K",
    "Dimmer PingPong": "Z",
    "Strobo ON": "S",
    "Strobo OFF": "D",
}
