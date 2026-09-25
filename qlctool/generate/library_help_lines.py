"""Which lines page 4's help carries: the built-in effects only where something has them.

The help spoke of "the panels' 42 built-in effects" and asked the operator to
watch them on a rig where nothing has built-in effects and no panels frame is
built (the small club, 2026-09-25, Plan C final review). None stands for a
separator, which is not a word.
"""


def library_help_lines(has_builtin_effects: bool) -> tuple[str | None, ...]:
    """The catalogue identifiers of page 4's help lines, in order, for this rig."""
    if has_builtin_effects:
        return (
            "library_1",
            "library_2",
            "library_3",
            None,
            "library_4",
            "library_5",
            None,
            "library_6",
            "library_7",
            None,
            "library_8",
            "library_9",
        )
    return (
        "library_1_no_builtins",
        "library_2_no_builtins",
        "library_3",
        None,
        "library_4",
        "library_5",
        None,
        "library_8",
        "library_9",
    )
