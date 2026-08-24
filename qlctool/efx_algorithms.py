"""The EFX movement algorithms QLC+ offers, and their show-facing names.

QLC+ matches `<Algorithm>` against these exact strings (Circle is the fallback
when it cannot). The Spanish labels are what the existing hand-built functions
call them ("Movimiento Circulo"), so generated names read the same on the
console.
"""

EFX_ALGORITHMS: tuple[str, ...] = (
    "Circle",
    "Eight",
    "Line",
    "Diamond",
    "Square",
    "Leaf",
    "Lissajous",
)

SPANISH_LABELS: dict[str, str] = {
    "Circle": "Circulo",
    "Eight": "Ocho",
    "Line": "Linea",
    "Diamond": "Diamante",
    "Square": "Cuadrado",
    "Leaf": "Hoja",
    "Lissajous": "Lissajous",
}
