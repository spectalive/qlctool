"""A stand-in for a running QLC+'s web API websocket, for the suite and CI.

It answers the `QLC+API|...` reads the way `webaccess/src/webaccess-qml.cpp`
does, applies `<widget>|<value>` presses and `setFunctionStatus`, records every
message it received, and pushes a console change to the client before each
answer - as the real one does to every client - so the live tools are held to
picking their reply out of the traffic.
"""

import threading

from websockets.sync.server import ServerConnection, serve

WIDGETS = {
    3: ["AUTO", "Button", "0", 21],
    4: ["Blackout", "Button", "0", 0],
    7: ["Master", "Slider", "255", 0],
}
FUNCTIONS = {21: ["Auto chase", "Chaser", False], 22: ["Rojo", "Scene", False]}


class FakeQlcPlus:
    """`with FakeQlcPlus() as qlc:` serves on a free localhost port, `qlc.port`."""

    def __init__(self) -> None:
        self.widgets = {wid: list(row) for wid, row in WIDGETS.items()}
        self.functions = {fid: list(row) for fid, row in FUNCTIONS.items()}
        self.received: list[str] = []
        self.silent = False

    def __enter__(self) -> "FakeQlcPlus":
        self._server = serve(self._handle, "127.0.0.1", 0, compression=None)
        self.port = self._server.socket.getsockname()[1]
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self._server.shutdown()
        self._thread.join()

    def _handle(self, connection: ServerConnection) -> None:
        for message in connection:
            assert isinstance(message, str)
            self.received.append(message)
            reply = self._reply(message.split("|"))
            if reply is not None and not self.silent:
                connection.send("3|BUTTON|0")
                connection.send(reply)

    def _reply(self, fields: list[str]) -> str | None:
        if fields[0] != "QLC+API":
            widget = self.widgets.get(int(fields[0]))
            if widget is not None:
                widget[2] = "255" if int(fields[1]) > 0 else "0"
            return None
        command, arguments = fields[1], fields[2:]
        head = f"QLC+API|{command}|"
        if command == "isProjectLoaded":
            return head + "true"
        if command == "getWidgetsList":
            return head + "|".join(f"{wid}|{row[0]}" for wid, row in self.widgets.items())
        if command == "getFunctionsList":
            return head + "|".join(f"{fid}|{row[0]}" for fid, row in self.functions.items())
        if command == "setFunctionStatus":
            self.functions[int(arguments[0])][2] = arguments[1] == "1"
            return None
        if command == "getChannelsValues":
            start, count = int(arguments[1]), int(arguments[2])
            return head + "|".join(
                f"{a}|{a % 256}|{'0.#FF0000' if a == 1 else ''}|0"
                for a in range(start, start + count)
            )
        return head + self._about(command, int(arguments[0]))

    def _about(self, command: str, number: int) -> str:
        widget = self.widgets.get(number)
        function = self.functions.get(number)
        if command == "getWidgetType":
            return f"{number}|{widget[1] if widget else 'Unknown'}"
        if command == "getWidgetStatus":
            return f"{number}|{widget[2]}" if widget else ""
        if command == "getWidgetFunction":
            fid = widget[3] if widget else 0
            if fid:
                return f"{number}|{fid}|{self.functions[fid][1]}|{self.functions[fid][0]}"
            return f"{number}|0|Undefined|"
        if command == "getFunctionType":
            return function[1] if function else "Undefined"
        return ("Running" if function[2] else "Stopped") if function else "Undefined"
