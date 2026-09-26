# qlctool

Programmatic editing of QLC+ workspaces (`.qxw`). A whole show is built for
any rig with at least one fixture group; `newshow` refuses a patch without one
with a message saying so. Movement is built only where some fixture pans and
tilts, and the dimmer chases only where some fixture has a fader dimmer, so a
pars-only or a washes-only rig gets a show too. Generates
scenes, chasers, RGBMatrix effects, movement EFX and the Virtual Console buttons
for them, in bulk instead of clicking them one by one in QLC+, then checks and
validates the result. The Vibra show it was built for is at
[github.com/Vibra-Lab/vibra-lighting](https://github.com/Vibra-Lab/vibra-lighting).

What the toolkit is for, the checks and the file format are documented in
[`docs/toolkit.md`](docs/toolkit.md).

## Why

The show has hundreds of hand-built functions. Repetitive work - a scene per
colour, a chaser cycling them, re-addressing the patch - is hours by hand and
seconds generated. The toolkit reads the real fixture definitions so it knows
which channel is red/dimmer/pan on each fixture, and writes changes back
surgically: a generated file differs from the original only by the functions it
added.

## Safety

Two nets. The first is a **semantic round-trip**: load then save never changes
what QLC+ reads (verified against the production workspaces in the test suite),
so a generator can only change the nodes it adds. The second is **headless
validation**: `qlctool validate` (or `--validate` on any command that writes)
loads the result in a real QLC+ with `--nowm --nogui` and fails on anything the
application complains about - a missing fixture definition, overlapping
addresses, a function it could not build. It loads a copy whose universes have
no input, output or feedback patch, an internal beat generator instead of the
microphone and no auto-starting network server, so the file itself asks QLC+ to
open none of the rig's connections - which also means it does not check that
I/O map. QLC+ also opens the default patches kept in its own settings, which a
copy cannot reach, so validation refuses to start while any exist
(`QLCTOOL_ALLOW_SAVED_IO=1` overrides). It stops only the QLC+ it started, by
that process's own pid, and QLC+ lists the copy among its recent files. Commands never overwrite the input -
they write a new `<name>-generado.qxw`.

Validation needs QLC+ installed; it looks in `/Applications/QLC+.app` and on
`PATH`, and `QLCTOOL_QLCPLUS` overrides both. The 4.x build (`qlcplus`) is
preferred because `--nogui` loads with no window at all; with only the 5.x QML
build (`qlcplus-qml`) validation still works; its window opens without taking focus. A missing QLC+ raises rather than
passing quietly. Custom fixture definitions must be installed in the QLC+ user
folder or every fixture that uses them reports "No fixture definition found" -
QLC+ 4 reads `~/Library/Application Support/QLC+/Fixtures` and QLC+ 5 reads
`~/Library/Application Support/QLC+ 5/Fixtures`.

## Install

```bash
pip install "qlctool @ git+https://github.com/spectalive/qlctool.git@v0.1.0"
```

Or, in a clone, for development:

```bash
python3 -m venv .venv && .venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest tests/ -q
```

The suite reads a frozen copy of the Vibra rig in `tests/data/rig/`.

The `mcp` extra (`pip install "qlctool[mcp] @ git+https://github.com/spectalive/qlctool.git@<tag>"`,
from `v0.1.7` on) adds `qlctool mcp`, an MCP server over stdio that
lets an agent build, check and validate shows and read a running QLC+ through
its web API - read-only unless started with `--allow-live-writes`. See
[`docs/mcp.md`](docs/mcp.md).

## Example

`examples/small-club/` is a small rig described in English: the fixture
definitions it uses, the patch, the description (`show.toml`) and the show
generated from them (`club.qxw`). From the repository root:

```bash
.venv/bin/qlctool newshow --description examples/small-club/show.toml --validate
```

## Use

```bash
# hand the installed QLC+ the rig's definitions, input profile and gobos
# (the folders its qlctool.toml names)
# (--check only reports what is stale or missing, exit 1 on any)
.venv/bin/qlctool install --check
.venv/bin/qlctool install

# list patched fixtures and the roles resolved for each
.venv/bin/qlctool info "path/to/DeluxeEventos2.qxw"

# generate 12 colour scenes + a cycle chaser into a new file
.venv/bin/qlctool palette "path/to/DeluxeEventos2.qxw"

# generate RGBMatrix effects: every algorithm x every palette colour, one group
.venv/bin/qlctool matrix "path/to/DeluxeEventos2.qxw" --group 0

# ...or a chosen subset ('solid' = plain colour matrix, no script)
.venv/bin/qlctool matrix "path/to/DeluxeEventos2.qxw" \
  --group 0 --algorithms "Strobe,Waves,solid"

# generate one movement EFX per shape across every moving head
.venv/bin/qlctool movement "path/to/DeluxeEventos2.qxw"

# check the patch for DMX address overlaps (exit 1 when it finds any)
.venv/bin/qlctool patch "path/to/DeluxeEventos2.qxw"

# edit the patch: add / re-address / rename / unpatch (addresses 1-based)
.venv/bin/qlctool patch "path/to/DeluxeEventos2.qxw" \
  --add "Vortex|PC-64 LED S|Default|0|301|PAR Extra" \
  --set-address "25=1:1" --rename "0=Wash Frontal 1" --remove 26

# place the rig the way it is really built (the plot lives with the show)
.venv/bin/qlctool stage "path/to/Vibra.qxw" \
  --plot "path/to/vibra-stage-plot.json"

# ...or let it arrange the fixtures by what they can do, when there is no plot
.venv/bin/qlctool stage "path/to/Vibra.qxw" --stage 12x6x8 --pov front

# build a fresh show on the same rig: patch kept, content regenerated.
# The plot must describe the patch the workspace actually has, or newshow
# refuses ("the plot places fixtures that are not patched: [27, 28]").
.venv/bin/qlctool newshow "path/to/Vibra.qxw" \
  --plot "path/to/vibra-stage-plot.json" \
  --out "path/to/Vibra.qxw" --validate

# ...the same show with the chases on the music's beat (needs an audio input
# picked in QLC+'s Configuration, or nothing advances)
.venv/bin/qlctool newshow "path/to/Vibra.qxw" --beats \
  --plot "path/to/vibra-stage-plot.json" \
  --out "path/to/Vibra-beats.qxw" --validate

# ...or from a show description: the patch stays in QLC+, the .toml says the
# rest (palette, matrices, timing, console, controllers). Names may be written
# in any shipped language: red, Red and rojo are the same colour.
# `[show] language = "en"` writes every generated name in English (patch names stay).
.venv/bin/qlctool newshow --description examples/small-club/show.toml --validate

# find out what each DMX channel of an undocumented fixture does, on site
.venv/bin/qlctool probe "path/to/DeluxeEventos2.qxw" 25 --base "1=255" --buttons

# add Virtual Console buttons for everything that has a UI folder
.venv/bin/qlctool layout "path/to/DeluxeEventos2.qxw"

# or generate and lay out in one run, then have QLC+ check the result
.venv/bin/qlctool palette "path/to/DeluxeEventos2.qxw" --buttons --validate

# load a workspace in headless QLC+ and report what it complains about
.venv/bin/qlctool validate "path/to/DeluxeEventos2.qxw"

# any command that writes a file can validate it in the same run
.venv/bin/qlctool movement "path/to/DeluxeEventos2.qxw" --validate

# split a show into a git-diffable fragment tree (one file per function)
.venv/bin/qlctool decompose "path/to/DeluxeEventos2.qxw" tree/

# rebuild a show from a fragment tree (semantically identical to the original)
.venv/bin/qlctool compose tree/ rebuilt.qxw
```

`decompose` writes `skeleton.qxw` (everything but the functions), one
`functions/NNNNN-Type-slug.xml` per function, and `manifest.json` recording the
Engine's child order. Edit or add fragment files, then `compose` to rebuild.
`decompose -> compose` is a verified lossless round trip.

A show description (`examples/small-club/show.toml` is a worked example; the
Vibra show's `QLC+ Setups/vibra.toml` in vibra-lighting is the full one) falls back
to Vibra's values for anything it leaves out, except `[controllers]`: leaving
that out means no MIDI pad and no tablet desk. What a stated key replaces:

- **Scalars merge key by key.** `[timing] bpm`, `beats`, `prism_step_s`,
  `matrix_beats`, every `[fixture_tuning]` key (and `strobe.fast` /
  `strobe.slow` on their own), `[console] canvas`, and `[palette] white` each
  replace just that value; the rest of the section keeps its default.
- **Named tables and lists replace whole.** `[palette.colors]`, `primary`,
  `simple`, `matrix_colors`, the three pair lists, `[console.keys]`,
  `flash_functions`, `[timing.beat_timings]` and `[groups]` (every group's
  matrices at once) are the whole thing when stated: a key in
  `[console.keys]` binds only the functions it lists. The duration tables
  `levels`, `dynamic` and `panels` are stated whole too, so each must give
  all its keys.
- **Inline tables inside `[timing]` and `[fixture_tuning]`.** `levels`,
  `dynamic` and `panels` are given whole; `strobe`, `matrix_beats` and each
  `[timing.beat_timings]` entry merge per key, so `colour_wheel = { hold = 4 }`
  keeps Vibra's fade. An entry for a function Vibra gives no timing needs a
  `hold`, and its `fade` defaults to 0.
- **One name, one row.** A table naming the same thing twice, even in two
  languages (`red` and `Rojo` in `[palette.colors]`), is refused with both
  spellings, the file and the section.
- **Vibra's matrices, only where the patch has the group.** Left out,
  `[groups]` means Vibra's hand-tuned matrices for each fixture group of the
  same name this patch has (`BarrasLed`, `Cabezas`, `PAR`); a group the patch
  lacks is skipped. A rig with a group of one of those names gets Vibra's
  scripts on it, and when the palette lacks a colour they use, the refusal
  names the group and asks you to state `[groups]`. An empty `[groups]` means
  no curated matrices at all.
- **The four-colour rig scenes need their colours.** The generator always
  deals blue, red, green and yellow in the `Rig 4 Colores` scenes, so a
  `[palette.colors]` without one of them is refused.

`[rig]` paths (`workspace`, `output`, `stage_plot`) resolve against the
description's own folder. Absolute paths and `..` are accepted, so a
description can read and write anywhere its user can: treat one you were sent
like a script, and read its `[rig]` before running it. `newshow --description`
writes to `--out` when given, else to `[rig] output`; with neither it refuses,
because it never overwrites the patch unasked. To regenerate a workspace in
place, state `output` equal to `workspace`, as Vibra's `vibra.toml` does.
A workspace given on the command line as well must be the one `[rig]` names.

## Layout

- `workspace.py`, `xmlsemantics.py`, `xmlutil.py` - load/save + the round-trip net
- `validate.py` - headless QLC+ load, the second safety net
- `skeleton.py` - strip a show back to its patch, for a fresh build
- `vc/` - Virtual Console widget builders (button, solo frame, appearance)
- `library.py`, `definition.py`, `roles.py` - fixture definitions and channel roles
- `fixture.py`, `capability.py`, `capabilities_of.py` - the patch and its capabilities
- `fixture_group.py`, `argb.py`, `matrix_algorithms.py` - RGBMatrix inputs
- `efx_algorithms.py` - EFX shapes and their Spanish show names
- `patch_conflicts.py`, `fixture_references.py`, `repatch/` - the patch layer:
  overlap detection, every node that points at a fixture, and the add /
  re-address / rename / remove operations
- `functions/` - Scene, Chaser, RGBMatrix and EFX element builders
- `generate/` - the mass generators (colour scene, colour palette, matrix
  effects, movement EFX, Virtual Console layout, channel probe)
- `palette.py`, `ids.py`, `cli.py` - palette data, ID allocation, command line
- `mcpserver/` - `qlctool mcp`: the file tools and the live QLC+ tools an agent calls ([`docs/mcp.md`](docs/mcp.md))
- `description/`, `names/`, `locales/`, `vibra/`, `controllers/` - the show description, its name catalogues, Vibra's values, and the optional controller profiles with their rule providers
- `library/system/` - QLC+ system fixture defs the patch needs, bundled from the Mac

## Fixture library note

`library/system/` holds three QLC+ built-in definitions the patch uses
(Stairville LED Bar 240, CLB2.4, Generic Smoke), copied from the show Mac's QLC+ install so the
capability layer resolves the whole patch without a QLC+ installation present.
A rig's own fixture definitions (the folders its `qlctool.toml` names, or
`--fixtures`, or `QLCTOOL_FIXTURES`) override system ones on a name clash.

## Licence

The code is under the Apache License 2.0 ([LICENSE](LICENSE)). The five
documents that came from the Vibra show's repository - `docs/toolkit.md`,
`docs/checks.md`, `docs/qxw-format.md`, `docs/qlcplus-environment.md` and
`docs/qlc5-verification.md` - are under CC BY 4.0
([LICENSE-CC-BY-4.0](LICENSE-CC-BY-4.0)), and so are the workspaces of the
frozen Vibra rig the tests read under `tests/data/rig/`; its fixture
definitions and input profile are Apache-2.0, two of the definitions QLC+'s
own ([NOTICE](NOTICE); its `README.txt` says which files carry which
licence). Everything else is Apache-2.0. The
QLC+ fixture schema and system fixture definitions vendored in
`qlctool/library/` are QLC+'s, under QLC+'s Apache License 2.0 ([NOTICE](NOTICE)).
