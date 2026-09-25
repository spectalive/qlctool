"""The kinds of thing a catalogue names, in catalogue order."""

SECTIONS: tuple[str, ...] = (
    "colors",
    "functions",
    "frames",
    "captions",
    "generated",
    "paths",
    "console",
    "help",
    "abbreviations",
    "mix_codes",
    # CLI and check text, not show vocabulary: nothing in a workspace is named from it.
    "messages",
)
