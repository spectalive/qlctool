"""The lines the QLC+ 5 QML build logs once a workspace is on screen.

It never goes quiet on its own, so this is what "loading finished" means
there: a Virtual Console page has rendered, which happens only after the
whole document - fixtures included - is loaded.

`MasterTimer is running late` and `Time is late` used to be in this tuple
too. Both come from the DMX output thread, which starts ticking as soon as
the engine starts and can print "running late" within milliseconds under any
CPU contention - well before the document, or its fixtures, are done
loading. Under concurrent validations (`test_two_validations_at_once_keep_
their_own_verdicts`) that marker fired before QLC+'s "No fixture definition"
line for a renamed fixture, so the quiet-period clock started too early and
validation stopped reading before the error was ever printed: a broken
workspace with no Virtual Console came back `ok` (2026-09-26). Measured: in
one full, unhurried log the timer's first "running late" line landed at
output line 134 while the fixture-load failure landed at line 138 -
consistently late enough to be missed under load, never early enough to help.
"""

QML_LOADED_MARKERS = ("renderPage",)
