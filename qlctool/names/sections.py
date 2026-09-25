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
    # What each `qlctool check` rule is called (ruling B10): a finding's `rule_id`.
    "checks",
    # What each finding says (ruling B10, round 2): a finding's `message_id`.
    "findings",
)
