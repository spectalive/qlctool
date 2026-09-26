"""Which lines page 4's help carries: the built-in effects only where something has them.

The help spoke of "the panels' 42 built-in effects" and asked the operator to
watch them on a rig where nothing has built-in effects and no panels frame is
built (the small club, 2026-09-25, Plan C final review). None stands for a
separator, which is not a word. Since the owner's delegated decision
(2026-09-25) the effects are "the panels'" only where a fixture is a panel
(`is_panel`); otherwise the same lines speak of them without that noun.

Since 2026-09-26 (round G review) the two-colour mixes and the matrices are
named only where their frames are drawn: one beam has no mix, two panels no
matrix, and the page draws no frame for either.
"""

from .store_suffix import store_suffix


def library_help_lines(
    has_builtin_effects: bool,
    has_panels: bool,
    has_mixes: bool = True,
    has_matrices: bool = True,
) -> tuple[str | None, ...]:
    """The catalogue identifiers of page 4's help lines, in order, for this rig."""
    suffix = store_suffix(has_mixes, has_matrices)
    # The arrows change a frame's group; with neither frame there is none.
    groups: tuple[str | None, ...] = (
        ("library_4", f"library_5{suffix}", None) if has_mixes or has_matrices else ()
    )
    if has_builtin_effects:
        return (
            f"library_1{suffix}",
            "library_2" if has_panels else "library_2_no_panels",
            "library_3",
            None,
            *groups,
            "library_6" if has_panels else "library_6_no_panels",
            "library_7",
            None,
            "library_8",
            "library_9",
        )
    return (
        f"library_1_no_builtins{suffix}",
        "library_2_no_builtins",
        "library_3",
        None,
        *groups,
        "library_8",
        "library_9",
    )
