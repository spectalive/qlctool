"""What `qlctool mcp` was started with: which QLC+ to talk to, and whether it may change it."""

from dataclasses import dataclass


@dataclass(frozen=True)
class McpSettings:
    """The server's options; `allow_writes` is off unless `--allow-live-writes` was given."""

    host: str = "127.0.0.1"
    port: int = 9999
    allow_writes: bool = False
    fixtures: tuple[str, ...] = ()
    timeout: float = 3.0

    @property
    def url(self) -> str:
        """The web API's websocket, as QLC+ serves it."""
        return f"ws://{self.host}:{self.port}/qlcplusWS"
