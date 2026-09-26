"""The catalogue suffix for page 4's lines that name what the store holds."""


def store_suffix(has_mixes: bool, has_matrices: bool) -> str:
    """ "" when both the mixes and the matrices frames are drawn, else what is missing."""
    return ("" if has_mixes else "_no_mixes") + ("" if has_matrices else "_no_matrices")
