"""The RGB script algorithms this show actually uses.

QLC+ resolves an `<Algorithm Type="Script">` by name against the RGB scripts
installed with the application, so these strings must match QLC+ exactly. This
list is every script name found in the production DeluxeEventos workspaces, so
each one is known to load on the show Mac.
"""

SCRIPT_ALGORITHMS: tuple[str, ...] = (
    "Alternate",
    "Even/Odd",
    "Fill",
    "Fill From Center",
    "Fill Unfill",
    "Gradient",
    "One By One",
    "Opposite",
    "Random Column",
    "Stripes From Center",
    "Strobe",
    "Waves",
)
