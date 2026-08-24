# `qlctool`

A Python library and CLI that edits QLC+ workspaces programmatically, in
`tools/qlctool/`. Setup and full command reference are in its own
[README](../tools/qlctool/README.md); this page is what it is *for* and what it
rests on.

## Why

The show has hundreds of hand-built functions. A scene per colour, a chaser
cycling them, matrix effects per group, movement over the heads, re-addressing
the patch, laying out two hundred console buttons - each is hours of clicking in
QLC+ and seconds generated. The toolkit reads the real fixture definitions, so
it knows which channel is red, dimmer, pan or gobo on each fixture, and writes
changes surgically: a generated file differs from the original only by what it
added.

## Two safety nets

1. **Semantic round-trip.** Load then save never changes what QLC+ reads -
   verified against every production workspace in the test suite. A generator
   can therefore only change the nodes it adds.
2. **Headless validation.** The result is loaded in a real QLC+ and any
   complaint fails the run. See
   [qlcplus-environment.md](qlcplus-environment.md).

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
| `patch` | Check the patch for address overlaps, or edit it: add, re-address, rename, unpatch |
| `layout` | Virtual Console buttons for every function, grouped by its UI folder |
| `newshow` | A whole self-running show built on an existing patch |
| `validate` | Load a workspace in headless QLC+ and report what it complains about |
| `decompose` / `compose` | Split a workspace into one file per function and rebuild it - a git-diffable source of truth |

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
