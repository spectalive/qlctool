# qlctool

Programmatic editing of QLC+ workspaces (`.qxw`) for the Vibra Eventos lighting
show. Generates scenes, chasers, RGBMatrix effects, movement EFX and the Virtual
Console buttons for them, in bulk instead of clicking them one by one in QLC+.

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
addresses, a function it could not build. Commands never overwrite the input -
they write a new `<name>-generado.qxw`.

Validation needs QLC+ installed; it looks in `/Applications/QLC+.app` and on
`PATH`, and `QLCTOOL_QLCPLUS` overrides both. The 4.x build (`qlcplus`) is
preferred because `--nogui` loads with no window at all; with only the 5.x QML
build (`qlcplus-qml`) validation still works but a window opens for a second. A missing QLC+ raises rather than
passing quietly. Custom fixture definitions must be installed in the QLC+ user
folder or every fixture in this rig reports "No fixture definition found" -
QLC+ 4 reads `~/Library/Application Support/QLC+/Fixtures` and QLC+ 5 reads
`~/Library/Application Support/QLC+ 5/Fixtures`.

## Setup

```bash
cd tools/qlctool
python3 -m venv --system-site-packages .venv   # lxml comes from the system
.venv/bin/pip install -e '.[dev]'
.venv/bin/pytest -q
```

## Use

```bash
# list patched fixtures and the roles resolved for each
.venv/bin/qlctool info "../../QLC+ Setups/DeluxeEventos2.qxw"

# generate 12 colour scenes + a cycle chaser into a new file
.venv/bin/qlctool palette "../../QLC+ Setups/DeluxeEventos2.qxw"

# generate RGBMatrix effects: every algorithm x every palette colour, one group
.venv/bin/qlctool matrix "../../QLC+ Setups/DeluxeEventos2.qxw" --group 0

# ...or a chosen subset ('solid' = plain colour matrix, no script)
.venv/bin/qlctool matrix "../../QLC+ Setups/DeluxeEventos2.qxw" \
  --group 0 --algorithms "Strobe,Waves,solid"

# generate one movement EFX per shape across every moving head
.venv/bin/qlctool movement "../../QLC+ Setups/DeluxeEventos2.qxw"

# check the patch for DMX address overlaps (exit 1 when it finds any)
.venv/bin/qlctool patch "../../QLC+ Setups/DeluxeEventos2.qxw"

# edit the patch: add / re-address / rename / unpatch (addresses 1-based)
.venv/bin/qlctool patch "../../QLC+ Setups/DeluxeEventos2.qxw" \
  --add "Vortex|PC-64 LED S|Default|0|301|PAR Extra" \
  --set-address "25=1:1" --rename "0=Wash Frontal 1" --remove 26

# find out what each DMX channel of an undocumented fixture does, on site
.venv/bin/qlctool probe "../../QLC+ Setups/DeluxeEventos2.qxw" 25 --base "1=255" --buttons

# add Virtual Console buttons for everything that has a UI folder
.venv/bin/qlctool layout "../../QLC+ Setups/DeluxeEventos2.qxw"

# or generate and lay out in one run, then have QLC+ check the result
.venv/bin/qlctool palette "../../QLC+ Setups/DeluxeEventos2.qxw" --buttons --validate

# load a workspace in headless QLC+ and report what it complains about
.venv/bin/qlctool validate "../../QLC+ Setups/DeluxeEventos2.qxw"

# any command that writes a file can validate it in the same run
.venv/bin/qlctool movement "../../QLC+ Setups/DeluxeEventos2.qxw" --validate

# split a show into a git-diffable fragment tree (one file per function)
.venv/bin/qlctool decompose "../../QLC+ Setups/DeluxeEventos2.qxw" tree/

# rebuild a show from a fragment tree (semantically identical to the original)
.venv/bin/qlctool compose tree/ rebuilt.qxw
```

`decompose` writes `skeleton.qxw` (everything but the functions), one
`functions/NNNNN-Type-slug.xml` per function, and `manifest.json` recording the
Engine's child order. Edit or add fragment files, then `compose` to rebuild.
`decompose -> compose` is a verified lossless round trip.

## Layout

- `workspace.py`, `xmlsemantics.py`, `xmlutil.py` - load/save + the round-trip net
- `validate.py` - headless QLC+ load, the second safety net
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
- `library/system/` - QLC+ system fixture defs the patch needs, bundled from the Mac

## Fixture library note

`library/system/` holds the two QLC+ built-in definitions the patch uses
(Stairville LED Bar 240, CLB2.4), copied from the show Mac's QLC+ install so the
capability layer resolves the whole patch without a QLC+ installation present.
Custom fixtures live in the repo's `QLC+ Fixtures/` and override system ones on a
name clash.
