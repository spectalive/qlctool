"""[palette]: the colours, and every subset and pairing drawn from them."""

from collections.abc import Mapping
from dataclasses import replace
from typing import Any

from ...color_pair import ColorPair
from ...generate.quad_color_scenes import QUAD_COLORS
from ...names.names import Names
from ..colour_settings import ColourSettings
from .identified_keys import identified_keys
from .list_at import list_at
from .named import named
from .reject_unknown_keys import reject_unknown_keys
from .rgb_value import rgb_value
from .table_at import table_at

LISTS = ("primary", "simple", "matrix_colors")
PAIRS = ("analogous_pairs", "key_split_pairs", "complementary_pairs")


def read_palette(
    table: Mapping[str, Any], base: ColourSettings, names: Names, where: str
) -> ColourSettings:
    """The base colours with every stated key replacing that whole table or list (R6, F7)."""
    here = f"{where}: [palette]"
    reject_unknown_keys(table, ("colors", "white", *LISTS, *PAIRS), here)
    changes: dict[str, Any] = {}
    if "colors" in table:
        colors = table_at(table, "colors", here)
        spelled = identified_keys(colors, names, "colors", f"{here} colors")
        changes["palette"] = {
            identifier: rgb_value(colors[spelling], f"{here} colors.{spelling}")
            for identifier, spelling in spelled.items()
        }
    for key in LISTS:
        if key in table:
            items = list_at(table, key, here)
            changes[key] = tuple(named(names, n, "colors", f"{here} {key}") for n in items)
    if "white" in table:
        changes["white"] = named(names, table["white"], "colors", f"{here} white")
    for key in PAIRS:
        if key in table:
            pairs: list[Any] = []
            for pair in list_at(table, key, here):
                if not isinstance(pair, list) or len(pair) != 2:
                    raise ValueError(f"{here} {key} holds [lead, bed] pairs, got {pair!r}")
                lead, bed = (named(names, n, "colors", f"{here} {key}") for n in pair)
                pairs.append((lead, bed) if key == "key_split_pairs" else ColorPair(lead, bed))
            changes[key] = tuple(pairs)
    colours = replace(base, **changes)
    used = [*colours.primary, *colours.simple, *colours.matrix_colors, colours.white]
    used += [n for pair in colours.key_split_pairs for n in pair]
    used += [
        n for p in (*colours.analogous_pairs, *colours.complementary_pairs) for n in (p.lead, p.bed)
    ]
    missing = sorted(set(used) - set(colours.palette))
    if missing:
        raise ValueError(f"{here} uses colours the palette does not have: {', '.join(missing)}")
    # The "Rig 4 Colores" scenes deal four fixed colours (R8 keeps them in the
    # generator), so a palette without one would only fail mid-build.
    dealt = [names.identify(n, ("colors",)) for n in QUAD_COLORS]
    lacking = [n for n in dealt if n not in colours.palette]
    if lacking:
        raise ValueError(
            f"{here} colors lacks {', '.join(lacking)}, which the four-colour rig scenes "
            f"always deal ({', '.join(dealt)})"
        )
    return colours
