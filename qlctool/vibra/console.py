"""The console the Vibra show is operated from."""

from ..description.console_settings import ConsoleSettings
from .flash_functions import FLASH_FUNCTIONS
from .keys import KEYS

# One 1440x900 screen: the show laptop's, and what live_console's layout is drawn for.
VIBRA_CONSOLE = ConsoleSettings(canvas=(1440, 900), keys=KEYS, flash_functions=FLASH_FUNCTIONS)
