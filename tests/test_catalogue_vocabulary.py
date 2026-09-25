"""The Spanish catalogue agrees with the Vibra show's own tables (2026-09-24).

The Vibra package names its functions and colours in Spanish; those names must
be exactly the catalogue's, or a key, a flash or a beat timing binds nothing.
The console's captions and frames no longer need a pin here: they are read
from the catalogue itself (Plan B, Task 9).
"""

from qlctool.names.load_catalogue import load_catalogue
from qlctool.palette import PALETTE
from qlctool.vibra.flash_functions import FLASH_FUNCTIONS
from qlctool.vibra.keys import KEYS
from qlctool.vibra.timing import VIBRA_TIMING

SPANISH = load_catalogue("es")


def test_the_spanish_colours_are_the_palette_in_order():
    assert list(SPANISH["colors"].values()) == list(PALETTE)


def test_every_function_the_vibra_tables_name_is_catalogued():
    named = set(KEYS) | set(FLASH_FUNCTIONS) | set(VIBRA_TIMING.beat_timings)
    assert named <= set(SPANISH["functions"].values())
