# qlctool mcp: the toolkit as an MCP server

`qlctool mcp` serves the toolkit to an agent over the Model Context Protocol's
stdio transport, so the agent can build a show, check it, validate it in QLC+,
and read - and, only when allowed, drive - a QLC+ that is running it.

## Install

The server is an optional extra. Plain `qlctool` never imports it:

```bash
pip install "qlctool[mcp] @ git+https://github.com/spectalive/qlctool.git@<tag>"
# or, in a clone
.venv/bin/pip install -e '.[mcp]'
```

`<tag>` is a release tag: the server ships from `v0.1.7` on, so use that tag
or a later one once it is released. qlctool is not on PyPI, so a bare
`pip install "qlctool[mcp]"` finds nothing.

The extra brings the official MCP Python SDK (`mcp` 2.2 or newer, whose
`MCPServer` is what 1.x called `FastMCP`) and `websockets` for the live tools.
Without it, `qlctool mcp` exits 1 and says which install it needs.

## Running it

```bash
qlctool mcp                                   # read-only, QLC+ web API at 127.0.0.1:9999
qlctool mcp --qlc-host 192.168.1.20 --qlc-port 9998
qlctool mcp --allow-live-writes               # live_press and live_function may act
qlctool --fixtures path/to/fixtures mcp       # the default fixture folders for the file tools
```

The server speaks on stdin and stdout; an MCP host starts it. For Claude Code:

```bash
claude mcp add qlctool -- qlctool mcp --qlc-port 9999
# driving the show as well as reading it:
claude mcp add qlctool-live -- qlctool mcp --qlc-port 9999 --allow-live-writes
```

or, in a project's `.mcp.json`:

```json
{
  "mcpServers": {
    "qlctool": {
      "command": "qlctool",
      "args": ["mcp", "--qlc-port", "9999"],
      "env": { "QLCTOOL_FIXTURES": "/path/to/QLC+ Fixtures" }
    }
  }
}
```

The fixture folders follow the CLI's order: `--fixtures`, a description's
`[rig] fixtures`, `QLCTOOL_FIXTURES`, then the nearest `qlctool.toml`.

## Tools

Paths may be absolute or relative to the directory the server was started in.
A path a tool reads must exist. A path a tool writes must sit in a folder that
exists, never inside the installed `qlctool` package, and never replaces an
existing file unless the call passes `overwrite=true`.

### Files

| Tool | Arguments | Returns |
| --- | --- | --- |
| `info` | `workspace` | patched fixtures (id, name, 1-based universe and address, model, mode, roles), fixture groups, models without a definition |
| `newshow` | `out`, `workspace?`, `description?`, `overwrite=false`, `buttons=true`, `validate=false` | the show `qlctool newshow` builds, written to `out`; counts, and QLC+'s verdict with `validate` |
| `check` | `workspace`, `description?`, `limit=200` | `clean`, the summary line `qlctool check` prints, and each finding: `rule_id`, `rule`, `severity`, `function`, `message`, `fixtures`, `fields` |
| `validate` | `workspace` | `ok` and QLC+'s complaints, from a QLC+ of the server's own loading an I/O-free copy |
| `deskmap` | `workspace`, `description?`, `out?`, `overwrite=false` | the tablet desk's map; with `out`, written there byte for byte as `qlctool deskmap` writes it |
| `pad_palette` | `workspace`, `out?`, `overwrite=false` | the SMC-PAD LED bridge's palette; with `out`, written as `qlctool pad-palette` writes it |

These call the same functions the CLI commands do; they are not subprocesses.

### A running QLC+

The live tools talk to QLC+'s web API websocket (`ws://HOST:PORT/qlcplusWS`),
which QLC+ serves when started with `-w` (and `--wp PORT`; the default is 9999).

| Tool | Arguments | Returns |
| --- | --- | --- |
| `live_status` | `workspace?` | `reachable`, `show_loaded` (it has functions), the function and widget counts, `writes_allowed`; with `workspace`, whether the running show is that file |
| `live_widgets` | `detail=true` | each widget's id and caption; with `detail`, its type, state and function |
| `live_functions` | `detail=false` | each function's id and name; with `detail`, its type and `running` |
| `live_channels` | `universe=1`, `start=1`, `count=16` | each channel's `address`, `value`, `group` and `overridden` (1-based, as the console numbers them) |
| `live_press` | `widget_id`, `value=255` | the widget's `type`, and its state `before` and after sending `<widget_id>\|<value>` |
| `live_function` | `function_id`, `state` (`on` or `off`) | the function's `type` and whether it is running afterwards |

The web API does not say which file QLC+ loaded, so `live_status` compares the
running show with `workspace` function by function: same ids, same names.
A widget's state is QLC+'s own: a button answers 255 active, 127 monitoring,
0 off; a slider its level; a cue list `PLAY|<step>` or `STOP`. Channel values
are read before the grand master. A channel's `group` is QLC+'s channel group
number, `0.#RRGGBB` for an intensity channel with its colour, or empty where
nothing is patched.

`live_status` does not ask QLC+ `isProjectLoaded`: QLC+ 5 answers a latch set
by a web upload, and QLC+ 4 clears it when asked. A running show has functions.

Names and captions come back as QLC+ sends them, `|`-separated and unescaped,
so a name holding `|` shifts the list after it and can read as an id that is
not there. The write tools therefore ask the target's own type
(`getWidgetType`, `getFunctionType`) before sending anything, and refuse an id
the running show does not have.

`live_press` sends a value only to a button or a slider, and refuses every
other widget type by name: the same `<id>|255` starts audio capture on an
Audio Triggers widget. QLC+ translates the type names, so the check knows
them in every language QLC+ 5 ships. It sends what the web console sends. A flash button takes 255 as a
press and 0 as a release. A toggle button flips on every message, 255 or 0
alike, and so does a blackout button (`VCButton::requestStateChange` in QLC+
5), so read `before` and send once. `live_function` starts or stops the
function itself, past the console: no button lights, and no solo frame stops
its neighbours.

## Safety

- **Read-only by default.** `live_press` and `live_function` refuse, naming
  `--allow-live-writes`, unless the server was started with that flag. The
  flag is the server's, not the call's: an agent cannot grant it to itself.
- **Nothing replaces a running show.** No tool loads, saves or replaces the
  workspace of a running QLC+, or touches its inputs, outputs or simple desk:
  the only messages sent are the API's reads, one widget value, and one
  function start or stop.
- **Files are never lost by accident.** Output paths refuse an existing file
  without `overwrite=true`, a missing folder, and the installed package.
- **Validation uses its own QLC+, offline.** `validate` (and `newshow` with
  `validate=true`) starts a QLC+ as its own child on a copy of the workspace
  whose universes have no `<Input>`, `<Output>` or `<Feedback>`, and stops
  exactly that process; a QLC+ somebody else runs, started before or during
  the validation, is never signalled. So validation no longer checks the I/O
  map the file names: QLC+ 5 has no way to load a workspace without opening
  its DMX, Art-Net and MIDI patches, and a validation run during a show must
  never take the rig's outputs. Both tools are annotated as not read-only
  and open-world for that reason.
- **Annotations.** The file writers (`newshow`, `deskmap`, `pad_palette`) are
  destructive, since `overwrite=true` replaces a file; `info` and `check` are
  read-only; `live_press` and `live_function` are destructive and open-world.

A QLC+ whose web access is password-protected answers nothing to an
unauthenticated client; the live tools then time out and say so.
