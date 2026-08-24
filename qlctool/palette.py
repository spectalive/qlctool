"""A standard colour palette for mass scene generation.

Names are Spanish to match the show's existing scene naming. Values are plain
8-bit RGB; the colour-scene generator turns each into the right per-fixture
channel values.
"""

PALETTE: dict[str, tuple[int, int, int]] = {
    "Rojo": (255, 0, 0),
    "Naranja": (255, 90, 0),
    "Amarillo": (255, 200, 0),
    "Verde": (0, 255, 0),
    "Cyan": (0, 255, 255),
    "Azul": (0, 0, 255),
    "Magenta": (255, 0, 255),
    "Rosa": (255, 40, 120),
    "Blanco": (255, 255, 255),
    "Ambar": (255, 140, 20),
    "Morado": (140, 0, 255),
    "Turquesa": (0, 200, 160),
}
