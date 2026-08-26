# What `qlctool check` looks for

`qlctool validate` asks QLC+ whether it can load a workspace. That is a low
bar: every bug this show has had loaded perfectly. `qlctool check` asks the
other question - **will the room do what the buttons promise** - and it asks it
of every button on the console.

```bash
qlctool check "QLC+ Setups/Vibra-split.qxw"
```

Every rule below exists because something went wrong in a real room. That is
the rule for adding one, too: find the cause, write a check that sees it, add a
regression test that puts the bug back, and run it over all three workspaces.

## How it reasons

Three ideas do all the work, and none of them involve a function's name.

**What a leaf function drives.** A Scene says exactly which channels it writes
and to what. An **EFX** writes pan/tilt, the dimmer, or RGB depending on each
fixture's `<Mode>`, and never a predictable value. An **RGBMatrix** writes red,
green and blue onto the heads of one fixture group and *nothing else* - not the
master dimmer, not the shutter. That last sentence is two of the bugs.

**What runs at the same instant.** A **Collection** starts all its members at
once, so they are concurrent. A **Chaser** plays its steps one at a time, so
steps are alternatives and never collide - which is exactly why the energy
levels are safe inside `Ciclo Energia` and were dangerous as three buttons.

**What answers for what.** The console is built around a solo frame: the room
is in exactly one **state** (AUTO, a moment, the work light, the blackout) and
everything else is a **layer** pressed on top. A state runs with nothing
underneath it, so it answers for every fixture it colours by any means. A layer
answers only for the colour it states itself, in a Scene - a matrix on the
library page is not asked to open a dimmer, because it cannot, and the state
beneath it already did.

## The rules

| Rule | What it catches | The night it comes from |
| --- | --- | --- |
| `intensidad` | A fixture given colour with nothing opening its dimmer, or with a labelled shutter left shut | The HYULIGHTS panels were the right colour and off all night (2026-08-26) |
| `rueda de color` | A look that colours a fixture group and writes nothing to the members of that group whose colour is a wheel | `BLANCO TOTAL` left the four BEAM 230W 7R black (2026-08-26) |
| `colores pisados` | Two concurrent members of one Collection reaching the same colour, wheel or pan/tilt channel | Two energy levels pressed at once turned the room white (2026-08-25) |
| `humo` | A scene that raises the smoke machine *and* touches other fixtures | A pump swept up in an "all dimmers up" scene runs until the tank is empty |
| `consola` | A master sharing a solo frame with its own members; two buttons on one key; a widget past the edge of the screen; one function with two buttons | AUTO died the instant it was pressed |

Dimmer and shutter collisions are **not** reported. QLC+ mixes intensity HTP on
purpose, and the whole design - a colour bed underneath, a level on top -
depends on two functions being able to ask for brightness at once.

## What it found on its first run

Four bugs, in a show that had already been fixed twice by hand:

- every per-group colour bank and every two-colour mix skipped the beams, so
  "the heads are red" left four of them on last night's colour;
- `Rueda Mezcla` did the same across the whole rig;
- every matrix button relied on a dimmer that nothing was opening;
- and once the banks were fixed, the beams turned out to be in two fixture
  groups at once, so two mix wheels wrote their colour wheel together.

The last one was a decision about the rig rather than the code, and it is the
shape these findings tend to have: the check does not fix anything, it turns
"a veces acertamos" into one question with a right answer.

## The one shutter subtlety

Whether a fixture is open depends on where its shutter *is*, not on whether
anybody wrote to it. A CLB2.4 head labels DMX 0 "no strobe", so an untouched
channel is already open; a BEAM 230W 7R puts open near the top, so an untouched
channel is shut. Only the labelled range separates those two, and reading it
wrong is either two hundred false alarms or a fixture dark that nobody warned
about.
