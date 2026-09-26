"""The environment validation starts QLC+ in, so its window never takes the screen."""

import os

# Measured 2026-09-26 on macOS with QLC+ 5.2.2's Cocoa build: launched
# directly it becomes the frontmost app about three seconds in; with these two
# Qt switches it loads the same way and focus never leaves what the owner was
# using. They mean nothing on other platforms.
QUIET = {
    "QT_MAC_DISABLE_FOREGROUND_APPLICATION_TRANSFORM": "1",
    "QT_MAC_SET_RAISE_PROCESS": "0",
}


def quiet_launch_environment() -> dict[str, str]:
    """This process's environment with the no-focus switches set."""
    return {**os.environ, **QUIET}
