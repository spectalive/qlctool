"""The EFX movement algorithms QLC+ offers.

QLC+ matches `<Algorithm>` against these exact strings (Circle is the fallback
when it cannot). The show-facing label of each shape is a catalogue word
(`efx_shape_identifiers`), so generated names read in the show's language.
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
