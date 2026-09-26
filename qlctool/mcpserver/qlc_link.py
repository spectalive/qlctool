"""One websocket conversation with a running QLC+'s web API.

QLC+ answers `QLC+API|<command>|...` with a message that starts the same way,
and in between it may push the console's own changes to every client, so a
reply is the next message with the command's prefix, not simply the next
message (`webaccess/src/webaccess-qml.cpp`, QLC+ 5). Widget presses and
`setFunctionStatus` get no answer at all.

Nothing here can load, save or replace a workspace: the only messages sent
are the API reads, a widget value and a function start or stop.
"""

import time
from contextlib import ExitStack
from types import TracebackType

from websockets.exceptions import WebSocketException
from websockets.sync.client import ClientConnection, connect

from .mcp_message import mcp_message
from .mcp_settings import McpSettings


class QlcLink:
    """A context manager: connect on entry, close on exit."""

    def __init__(self, settings: McpSettings) -> None:
        self.settings = settings
        self._socket: ClientConnection | None = None
        self._stack = ExitStack()

    def __enter__(self) -> "QlcLink":
        try:
            # Entered as a context manager: websockets 17 deprecates a bare connect().
            self._socket = self._stack.enter_context(
                connect(
                    self.settings.url,
                    open_timeout=self.settings.timeout,
                    compression=None,
                    ping_interval=None,
                    max_size=2**24,
                )
            )
        except (OSError, TimeoutError, WebSocketException) as error:
            message = mcp_message("mcp_live_unreachable", url=self.settings.url, error=error)
            raise ConnectionError(message) from error
        return self

    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        trace: TracebackType | None,
    ) -> None:
        self._socket = None
        self._stack.close()

    def send(self, message: str) -> None:
        """Send one message that QLC+ does not answer."""
        assert self._socket is not None, "QlcLink used outside its with block"
        self._socket.send(message)

    def ask(self, command: str, *arguments: object) -> list[str]:
        """The fields of QLC+'s answer to `QLC+API|command|arguments...`."""
        assert self._socket is not None, "QlcLink used outside its with block"
        prefix = f"QLC+API|{command}|"
        self._socket.send("|".join(["QLC+API", command, *(str(a) for a in arguments)]))
        deadline = time.monotonic() + self.settings.timeout
        while (left := deadline - time.monotonic()) > 0:
            try:
                reply = self._socket.recv(timeout=left)
            except TimeoutError:
                break
            if isinstance(reply, str) and reply.startswith(prefix):
                return reply[len(prefix) :].split("|")
        raise TimeoutError(
            mcp_message(
                "mcp_live_no_reply",
                url=self.settings.url,
                command=command,
                seconds=self.settings.timeout,
            )
        )
