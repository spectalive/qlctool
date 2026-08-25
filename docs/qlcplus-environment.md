# The QLC+ environment

## Versions in play

- The workspaces in `QLC+ Setups/` are saved in **4.13.1** format; one copy each
  in 4.14.3 and 5.2.2 is kept as test material.
- The show machine runs **QLC+ 5.2.2** (`qlcplus-qml`, the QML build).
- QLC+ 5 opens 4.x workspaces on load.

## Custom fixture definitions must be installed

The seven `.qxf` in `QLC+ Fixtures/` are not part of QLC+'s library. Until they
are copied into the QLC+ **user fixture folder**, opening a show reports
`No fixture definition found` for every fixture that uses them - except
CromoWash100, which QLC+ 5 ships itself.

| Platform / version | Folder |
| --- | --- |
| macOS, QLC+ 4 | `~/Library/Application Support/QLC+/Fixtures` |
| macOS, QLC+ 5 | `~/Library/Application Support/QLC+/Fixtures` (a `QLC+ 5` folder also exists on some installs; copying to both is harmless) |
| Bundled library | `/Applications/QLC+.app/Contents/Resources/Fixtures/<Manufacturer>/` |

## Gobo images have to be installed too

A definition's gobo thumbnails are a `Res1` path per capability. An **absolute**
path is used as it stands - which is why `~/Desktop/Gobos/...` worked on one
machine and nowhere else. A **relative** path is resolved against QLC+'s own
Gobos folder, and there is no user-level equivalent
(`QLCCapability::loadXML` -> `QLCFile::systemDirectory(GOBODIR)`), so the images
go inside the bundle:

```bash
cp -R "QLC+ Setups/Gobos/BEAM-LIGHT-230W-7R" \
  "/Applications/QLC+.app/Contents/Resources/Gobos/BEAM-230W-7R"
```

Redo it after a QLC+ upgrade - upgrading replaces the bundle. A missing file
costs a thumbnail and nothing else; QLC+ does not complain.

QLC+ caches the library at start, so **restart it** after copying definitions in.
A definition present in both the user folder and the bundled library logs
`Cache already contains "<name>"`, which is harmless.

## Headless validation

QLC+ itself is the strongest check available, and it can be driven from a
script.

```bash
# 4.x widgets build: loads with no window at all
qlcplus --nowm --nogui -d 1 -o show.qxw

# 5.x QML build: no headless mode - a window opens for a moment
qlcplus-qml -d -m -o show.qxw
```

Neither exits on its own: QLC+ loads the workspace, starts its engine and stays
up. So the verdict comes from the log, not from the exit code, and the process
is killed once loading is done - the 4.x build falls silent, the QML build keeps
logging as it renders and is stopped shortly after its end-of-load markers.

Lines that mean the workspace is wrong:

```
No fixture definition found for <model>
bool Doc::addFixture(...) fixture 13 overlapping with fixture 0 @ channel 0
static bool Fixture::loader(...) Fixture "CromoWash100 #3" cannot be created.
<n> channels of fixture <name> are out of bounds
```

### Without it taking the screen

The QML build opens a window, and on macOS that pulls focus away from whatever
you were doing - once per generated file, which makes a test run unusable. So on
macOS `validate` launches the bundle with `open -g`, which starts it in the
background, and tells QLC+ to write its debug log to a file (`-g`, always
`~/QLC+.log`) because `open` hands back no stdout. Only the processes that call
started are killed afterwards, so a QLC+ you have open yourself survives.

`open` refuses (`-600`) while a copy is still shutting down; the run then falls
back to the foreground launch rather than reporting a false pass. Set
`QLCTOOL_FOREGROUND=1` to always use the foreground path.

**A QLC+ you already have open does the same thing more quietly.** `open -g`
activates that instance instead of starting one, returns 0, and writes nothing
to the log file - so the validator had a way to come back
`ok=True, errors=[], log=''` from a run that never happened, which is the exact
failure the whole net exists to prevent. Two guards now: the background path
gives up and falls back when it never sees an end-of-load marker, and an empty
log raises instead of passing. QLC+ prints its banner before it does anything,
so a real run is never silent.

### Reading the source

QLC+ is open source and the answer to "what does this tag actually do" is in it.
A shallow clone of `mcallegari/qlcplus` lives outside this repository; the files
worth knowing are `engine/src/chaserrunner.cpp` (step timing),
`ui/src/virtualconsole/` and `qmlui/virtualconsole/` (the two Virtual Console
implementations, whose XML is the same).

`qlctool validate <file>` does all of this, and `--validate` on any command that
writes a workspace does it to the result. It looks for QLC+ in
`/Applications/QLC+.app` and on `PATH`; `QLCTOOL_QLCPLUS` overrides both. **A
missing QLC+ raises rather than passing**, so an uninstalled validator can never
be mistaken for a clean run.

## Machines

Two Macs are involved: a workstation where the toolkit is developed, and the
show laptop at the venue. Their addresses, accounts and access live in the
owner's private notes, not in this public repository.

One trap worth recording without those details: the show laptop has no Xcode
Command Line Tools, so Apple's `/usr/bin/git` (and `strings`, and friends) fail
with `xcrun: error: invalid active developer path`. Homebrew's git is installed
and comes first on the interactive PATH, so a normal terminal session is fine -
only non-interactive remote commands hit the broken shim, and they need the
Homebrew prefix put on PATH first.
