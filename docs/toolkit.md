# `qlctool`

A Python library and CLI that edits QLC+ workspaces programmatically. Setup
and full command reference are in its
[README](../README.md); this page is what it is *for* and what it
rests on.

## Why

The show has hundreds of hand-built functions. A scene per colour, a chaser
cycling them, matrix effects per group, movement over the heads, re-addressing
the patch, laying out two hundred console buttons - each is hours of clicking in
QLC+ and seconds generated. The toolkit reads the real fixture definitions, so
it knows which channel is red, dimmer, pan or gobo on each fixture, and writes
changes surgically: a generated file differs from the original only by what it
added.

## Three safety nets

1. **Semantic round-trip.** Load then save never changes what QLC+ reads -
   verified against every production workspace in the test suite. A generator
   can therefore only change the nodes it adds.
2. **Headless validation.** The result is loaded in a real QLC+ and any
   complaint fails the run. See
   [qlcplus-environment.md](qlcplus-environment.md).
3. **Schema validation of the fixture definitions.** Every `.qxf` in
   `QLC+ Fixtures/` is checked against `fixture.xsd`, QLC+'s own schema,
   vendored into the toolkit. QLC+ itself never refuses a definition it
   dislikes - it drops the parts it cannot read and carries on - so without
   this the damage is invisible. It found a `Weight="0"` that had been there
   since the definition was written.

On top of both: every generator is tested against the real shows, and the
builders are proved by **rebuilding the show's own functions node for node** -
all 122 RGBMatrix and all 30 EFX, in each of the three saved formats. If an
attribute, a child order or a colour encoding were wrong, those tests fail.

Commands never overwrite their input; they write a new file.

## What it can do

| Command | Purpose |
| --- | --- |
| `info` | The patch and the roles resolved for each fixture, plus the fixture groups |
| `palette` | Colour scenes across every colour-capable fixture, plus a cycle chaser |
| `matrix` | RGBMatrix effects, algorithm x colour, for one fixture group |
| `movement` | One EFX per shape across every moving head, phases spread |
| `probe` | One scene per DMX channel of a fixture - how an undocumented fixture gets settled on site |
| `patch` | Check the patch for address overlaps, or edit it: add, re-address, rename, unpatch, and put fixtures in a group or resize its grid |
| `layout` | Virtual Console buttons for every function, grouped by its UI folder |
| `stage` | A position for every fixture in the 2D/3D view - `--plot` applies the real montage, without it the layout is generated from what each fixture can do |
| `mvr` | The placed rig as an MVR package for BlenderDMX, with a GDTF generated from each fixture definition inside it - geometry, wheels with the gobo images, one DMX mode per QLC+ mode ([blenderdmx.md](https://github.com/Vibra-Lab/vibra-lighting/blob/main/docs/blenderdmx.md)) |
| `newshow` | A whole self-running show built on an existing patch, plus the four-page live console (show / JUGAR / control / library) on one screen. A patch with no fixture group of two or more fixtures is refused before anything is generated, with a message saying so; one whose definitions are not found is told that instead. A rig with nothing that pans and tilts gets no movement, and one with no fader dimmer no dimmer chase |
| `check` | What the room will actually do: fixtures coloured but never lit, colour a fixture can only take on a wheel, two programmes writing one channel, and the console's own traps ([checks.md](checks.md)) |
| | (rig-wide colour wheel, colour banks and mixes, matrices, movement mirrored side to side, gobos, beam colour, prism, smoke, dimmer chase and ping-pong, shutter and flash strobes, and the energy levels `AUTO` walks through - `--beats` puts the lot on the music's beat) |
| `validate` | Load a workspace in headless QLC+ and report what it complains about |
| `install` | Hand the installed QLC+ the configured fixture definitions, input profiles and gobo images; `--check` reports the copies that are stale or missing and exits 1, because QLC+ runs on copies and never says when they are behind |
| `decompose` / `compose` | Split a workspace into one file per function and rebuild it - a git-diffable source of truth |

## Where the toolkit finds your files

The toolkit assumes nothing about where a rig keeps its fixture definitions.
The first of these sources that names any folder wins:

1. `qlctool --fixtures DIR`, repeatable, before the subcommand.
2. The description's `[rig] fixtures = ["dir", ...]`, relative to the
   description file.
3. `QLCTOOL_FIXTURES`, folders separated by `:` (`;` on Windows).
4. The nearest `qlctool.toml` found by walking up from the workspace (a
   description beside it shares that folder), and failing that from the
   current directory.

Within one source the first folder wins a model clash, and every one of them
beats the QLC+ system definitions bundled with the toolkit. A patched fixture
with no definition is a warning on stderr naming the fixtures and the folders
searched. `qlctool install` reads the same file for the input profiles and
gobo images it copies. A rig's `qlctool.toml`, as the Vibra show's reads
(a frozen copy sits in `tests/data/rig/` for the tests):

```toml
# Where qlctool finds this rig's own files (spec step 6). Paths are
# relative to this file. Overridden by `qlctool --fixtures`, a description's
# [rig] fixtures, or QLCTOOL_FIXTURES, in that order.
fixtures = ["QLC+ Fixtures"]
input_profiles = ["QLC+ InputProfiles"]
gobos = ["QLC+ Setups/Gobos"]
```

## Languages

A description's `[show] language` picks the language the show is written in:
`en` or `es` (Spanish when it does not say). The words of a generated show -
functions, paths, console frames, captions, the JUGAR page and the desk map -
come from `qlctool/locales/<lang>.toml`, with these exceptions. The standalone
`palette`, `matrix`, `movement`, `probe` and `layout` commands still write
Spanish (ruling B5). The patch's own fixture and group names, and the wheel
slot names of the fixture definitions, stay as they were patched. A few
language-neutral words come from no catalogue, because they are spelled the
same in both (ruling B6): the `Rig` prefix of the unison colour scenes, the
`Show`, `Dimmers` and `Desk` function folders, `Solid` for a matrix with no algorithm,
the `Wash` and `Beam` movement prefixes (no catalogue entry renders them
alone; `prefix_fast_wash` is "Wash Rapido" / "Fast Wash"), `Gobo Shake - `,
and the `(8 bit)` / `(16 bit)` suffixes of a split EFX. The root console
frame's caption comes from the catalogue too (`root_frame`: "Page 1" /
"Página 1"), whatever the input workspace called it.

`[names.<lang>]` overrides any identifier; an override of a template must keep
its `{fields}`. An override of a `frames` identifier may reword the explanation
after " — " but not the head before it: `qlctool check` and the desk find
frames by their shipped head, so a renamed head is refused while the
description is read. `qlctool check` messages are still Spanish on any show
(ruling B10, open in the Vibra show's
[`TODO.md`](https://github.com/Vibra-Lab/vibra-lighting/blob/main/TODO.md)).

## Examples

`examples/small-club/` is a second rig, described in English:
six RGB pars, two beam moving heads with no gobo, prism or colour wheel, and
two washes. It is a different patch from the Vibra show's: three of Vibra's
models in other numbers, addresses and groups, with no haze machine and no
controllers. It holds the three fixture definitions it uses (`fixtures/`),
the patch (`club-patch.qxw`), the description (`show.toml`, which states
`language = "en"` and names no `[controllers]`) and the show generated from
them (`club.qxw`, never edited by hand). Regenerate it from
the repository root:

```bash
qlctool newshow --description examples/small-club/show.toml --validate
qlctool --fixtures examples/small-club/fixtures check examples/small-club/club.qxw
```

`tests/test_small_club_example.py` regenerates it and holds it byte-for-byte
against the committed `club.qxw`, runs every check over it with no finding,
asserts it carries no pad binding, desk function or controller rules, and
loads it in QLC+.

## Design notes worth keeping

- **Fixtures are selected by capability, never by name or ID list.** "Every
  fixture that has pan and tilt", "every fixture with a gobo wheel". A re-patch
  cannot invalidate that.
- **Channel counts come from the definition's mode**, never from the caller: a
  wrong width silently shifts every fixture after it on the universe.
- **Every patch mutation re-checks the whole patch** and rolls itself back on a
  collision.
- **Addresses are 0-based in the library and in the file, 1-based on the command
  line** - the same way QLC+ shows them.
- **Smoke machines are excluded everywhere** except the smoke generator.
- **A fixture in no group gets almost nothing.** Colour banks and matrices
  are both built per group, so patching a fixture is only half of adding it.
- **One EFX cannot hold two kinds of fixture.** One whose fine channels are
  not adjacent to their coarse ones turns 16-bit off for the *whole* EFX,
  because the flag lives on the EFX's fader rather than on the fixture.
  `efx_16bit` says which side a fixture falls on, for pan and tilt or for
  intensity; movement and the dimmer chase are both generated per group and run
  from a Collection, so the console still sees one function per look.
- **One answer to "what value opens this shutter".** `shutter_open_pairs` reads
  it out of the definition, and both the scenes that raise a fixture and the
  strobe that has to reopen one use it.
- **A dimmer at full is not a light that is on.** A fixture with a mechanical
  shutter needs it opened as well, and the value comes from the definition's own
  `ShutterOpen` range. Every generator that raises a dimmer calls
  `shutter_open_pairs`.
- **A role can land on two channels of one fixture, and only one of them is the
  wheel.** The colour wheel and the continuous half-colour channel beside it are
  both in the Colour group. Wheel scenes drive
  `wheel_for_role` - the channel that actually carries the labelled positions -
  never every channel that shares the role.
- **The 2D/3D plot is generated from capability too**: gobo wheel means beam
  and hangs upstage, pan+tilt without one means wash and hangs downstage, a
  bar lies on the floor at the back, everything else stands at the front.
