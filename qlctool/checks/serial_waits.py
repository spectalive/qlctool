"""Whether a head of a Serial EFX waits for its turn, written by nobody.

A Serial EFX delays fixture k by loopDuration/(fixtureCount+1)*k, and until
then `EFXFixture::nextStep` returns without writing anything
(`efxfixture.cpp`: "Bail out without doing anything if this fixture is waiting
for its turn"). Only the first head starts at once. On Vibra that left MAC #1
and #2 at 127/127 for 10 and 11.6 s at the start of `Ola Vertical` (en-sala
DMX audit, 2026-09-26). Asymmetric propagation phases the heads the same way
without the wait.
"""

from lxml import etree

from ..xmlutil import find_local, findall_local


def serial_waits(efx: etree._Element, fixture_id: int) -> bool:
    """True when `efx` is Serial and `fixture_id` is not its first head."""
    mode = find_local(efx, "PropagationMode")
    if mode is None or (mode.text or "").strip() != "Serial":
        return False
    for index, element in enumerate(findall_local(efx, "Fixture")):
        identifier = find_local(element, "ID")
        if identifier is not None and (identifier.text or "").strip() == str(fixture_id):
            return index > 0
    return False
