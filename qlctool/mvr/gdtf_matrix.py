"""A GDTF geometry position: a translation in metres and an optional flip.

GDTF writes a geometry's place under its parent as a 4x4 matrix, row-major with
the translation in the last column, and BlenderDMX reads it back exactly so
(`add_child_position` in its `gdtf.py`: `to_translation()` for the offset, the
3x3 part - inverted - for the rotation). The only rotation this export ever
needs is a half turn about X, which is its own inverse, so the inversion
changes nothing. A beam geometry emits along its own -Z; flipped, it emits
along the fixture's +Z, away from the base, which is how every fixture here is
modelled: standing, lens up.
"""

from pygdtf import Matrix


def gdtf_matrix(x: float, y: float, z: float, flipped: bool = False) -> Matrix:
    """Translation (metres) under the parent, flipped a half turn about X or not."""
    s = -1.0 if flipped else 1.0
    return Matrix(f"{{1,0,0,{x:.6f}}}{{0,{s:g},0,{y:.6f}}}{{0,0,{s:g},{z:.6f}}}{{0,0,0,1}}")
