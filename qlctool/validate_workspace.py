"""Load a workspace in a real QLC+ and report what it complained about.

The toolkit's other guarantee is structural: a semantic round trip proves an
edit changed only what it targeted, but it cannot prove QLC+ accepts the result.
This runs the actual application, which loads the workspace and logs every
problem it finds - a fixture whose definition is missing, two fixtures
overlapping, a function it could not build.

QLC+ has no "load and exit" mode: it starts its engine and stays up. So it is
launched, watched until loading is done, then killed, and the verdict comes from
its log rather than the exit code.

What QLC+ loads is an offline copy (`validation_copy`, `offline_workspace`):
every universe kept, its `<Input>`, `<Output>` and `<Feedback>` removed, an
audio beat generator made internal, a network server's autostart off, and its
`CurrentWindow` forced to `VC` so the QML build's end-of-load marker, which
only ever logs there, is not missed on a workspace saved on another view
(`force_vc_window`; C-1, 2026-09-27 final review). A
validation run during a show must never open the rig's DMX interface,
Art-Net, MIDI or the microphone again, and QLC+ 5 has no flag to load without
them - so validation no longer checks the I/O map the file names (2026-09-26,
reviews of round D6). The default patches QLC+ keeps in its own settings are
beyond a copy's reach: validation refuses to start while any exist
(`refuse_saved_io`). QLC+ also records the copy in its recent-files list,
which is not restored. The only process it stops is
the one it started, by that child's exact pid (`stop_own_process`).

Two builds behave differently. The 4.x widgets build (`qlcplus`) takes
`--nogui`, loads with no window at all, and then falls silent - that is the one
to prefer. The 5.x QML build (`qlcplus-qml`) has no headless mode: it opens a
window, kept from taking the screen by `quiet_launch_environment`, and keeps
logging while it renders, so loading is considered finished once its
end-of-load markers appear and the log settles.

Versioned bundles in /Applications are found too, newest first, and a binary
this CPU cannot run is skipped (`qlcplus_candidates`).
"""

from pathlib import Path

from lxml import etree

from .qlcplus_binary import qlcplus_binary
from .refuse_saved_io import refuse_saved_io
from .run_qlcplus import run_qlcplus
from .validation_copy import validation_copy
from .validation_result import ValidationResult
from .validation_verdict import validation_verdict


def validate_workspace(
    path: str | Path,
    binary: str | None = None,
    timeout: float = 30.0,
    quiet_period: float = 1.0,
    allow_saved_io: bool = False,
) -> ValidationResult:
    """Load an offline copy of the workspace in QLC+ and collect its complaints.

    Raises FileNotFoundError when no QLC+ is installed - a missing validator must
    never read as a passing validation.

    `quiet_period` is how long after the end-of-load markers the log is still
    read. Measured over nine launches of the QML build (2026-09-22): a fixture
    complaint lands in the same 20 ms as the first marker and the log stops
    growing 0,2 s after it, so one second is a fivefold margin - and half of
    what every validation used to wait.

    Raises RuntimeError, before QLC+ is started, when QLC+'s own settings
    hold default I/O patches it would open at startup (`refuse_saved_io`),
    unless `allow_saved_io` or `QLCTOOL_ALLOW_SAVED_IO=1` says to go ahead.
    QLC+ adds each file it loads to its recent-files list; validation does
    not restore that list.
    """
    path = Path(path).resolve()
    executable = binary or qlcplus_binary()
    if executable is None:
        raise FileNotFoundError("no QLC+ executable found; set QLCTOOL_QLCPLUS to its path")

    qml = Path(executable).name.endswith("-qml")
    refuse_saved_io(allow_saved_io)
    try:
        with validation_copy(path) as copy:
            log = run_qlcplus(executable, copy, qml, timeout, quiet_period)
    except etree.XMLSyntaxError as error:
        # QLC+ reads a broken file up to the break, I/O patches included, so it
        # is never handed one: the syntax error is the verdict.
        return ValidationResult(ok=False, errors=[f"not well-formed XML: {error}"])
    verdict = validation_verdict(log.text)
    if log.marker_seen:
        return verdict
    # A QML load that never logged its end-of-load marker did not finish:
    # whatever it printed before the timeout is not a verdict on the file
    # (2026-09-26, second review of round D6).
    unfinished = (
        f"QLC+ exited before its end-of-load marker (exit code {log.exit_code})"
        if log.exit_code is not None
        else f"QLC+ never finished loading: no end-of-load marker within {timeout:g} s"
    )
    return ValidationResult(ok=False, errors=[unfinished, *verdict.errors], log=verdict.log)
