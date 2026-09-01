"""The colour palette, taken from the colours the real show actually uses.

Mined from DeluxeEventos2 (2026-08-24): every distinct RGB triple its 190 scenes
drive, plus the colours of its 122 matrices. That is why the odd values are here
- (255, 0, 100) and (160, 0, 255) are the owner's, not a designer's guess - and
why a generated show looks like the hand-built one instead of like a test
pattern. Names follow the show's own Spanish vocabulary.
"""

PALETTE: dict[str, tuple[int, int, int]] = {
    "Rojo": (255, 0, 0),
    "Rojo Fuego": (255, 20, 0),
    "Naranja": (255, 127, 0),
    "Ambar": (255, 183, 0),
    "Amarillo": (255, 255, 0),
    "Verde": (0, 255, 0),
    "Verde Menta": (0, 255, 128),
    "Cyan": (0, 255, 255),
    "Celeste": (0, 200, 255),
    "Azul Cielo": (0, 127, 255),
    "Azul": (0, 0, 255),
    "Azul Profundo": (0, 35, 255),
    "Morado": (85, 0, 255),
    "UltraVioleta": (160, 0, 255),
    "Magenta": (255, 0, 255),
    "Fucsia": (255, 0, 176),
    "Rosa": (255, 0, 100),
    "Blanco": (255, 255, 255),
}

# The colours the show leans on hardest, for banks that must stay one screen
# wide (the original's colour buttons are keys 1-9 and 0).
PRIMARY_COLORS: tuple[str, ...] = (
    "Rojo",
    "Verde",
    "Azul",
    "UltraVioleta",
    "Amarillo",
    "Cyan",
    "Magenta",
    "Blanco",
    "Naranja",
    "Rosa",
)
