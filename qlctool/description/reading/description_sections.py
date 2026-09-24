"""The top-level sections a show description may have."""

DESCRIPTION_SECTIONS: frozenset[str] = frozenset(
    {
        "show",
        "rig",
        "palette",
        "groups",
        "timing",
        "fixture_tuning",
        "console",
        "controllers",
        "names",
    }
)
