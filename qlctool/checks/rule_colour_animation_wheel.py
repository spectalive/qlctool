"""A colour *animation* that leaves the wheel-coloured fixtures on one colour.

`rule_wheel_colour` asks whether a look ever states a colour on the beams, and
it counts only Scenes, for a good reason: a matrix paints a group's pixels and
can say nothing about a member that has none. An EFX is different. It lists the
fixtures it drives, one `<Fixture>` each, so a fixture it omits is a decision
nobody made - and nothing was checking those. The two rainbows are relative EFX
in RGB mode over "every RGB head" (`rainbow_efx.py` counts red channels and
finds none on a 7R), so `Arcoiris Simultaneo` sweeps the whole room through the
spectrum with the four beams nailed to whatever colour they had: "el arcoiris
no funciona con los beam, no hace el color arcoiris" (owner, 2026-09-22).

The claim is read per fixture group, exactly as `rule_wheel_colour` reads it: a
look that animates the colour of a group has made a claim about that group, and
the four beams are *in* Cabezas beside the washes. That the state underneath
keeps stepping their wheel every 2,5 s is no defence - the room then shows a
spectrum sweeping over four fixtures walking a different clock, which is the
"no hace el color arcoiris" the owner saw.

A fixture whose colour is a wheel can animate colour - the BEAM 230W 7R carries
a continuous rainbow spin at 128-191 of its colour channel, and a chaser can
step the wheel detent by detent. So the rule is not "the wheel was written": it
is that a look which animates colour on the RGB fixtures must animate it on the
wheel ones too, by a rotation range or by more than one value across the look.
A single static detent under a running rainbow is the bug, not the fix.
"""

from lxml import etree

from .. import roles
from ..capability import FixtureCapabilities
from ..xmlutil import find_local, iter_local
from .driven_channels import driven_channels
from .finding import ERROR, Finding
from .show_graph import ShowGraph, lit

RULE_ID = "colour_animation_wheel"
EFX_RGB_MODE = "2"  # EFXFixture::Mode - PanTilt, Dimmer, RGB
ROTATION = "Rotation"


def check_colour_animation_wheel(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], entries: dict[int, str]
) -> list[Finding]:
    findings: list[Finding] = []
    for function_id, caption in sorted(entries.items()):
        animated = _animated_rgb_fixtures(graph, groups, function_id)
        if not animated:
            continue
        claimed: set[int] = set()
        for members in groups.values():
            if animated & set(members):
                claimed |= set(members)
        stuck = sorted(
            graph.capabilities[fixture_id].fixture.name
            for fixture_id in claimed
            if _wheel_coloured(graph, fixture_id)
            and not _wheel_animated(graph, groups, function_id, fixture_id)
        )
        if not stuck:
            continue
        findings.append(
            Finding(
                rule_id=RULE_ID,
                severity=ERROR,
                function=caption,
                fixtures=tuple(stuck),
                message_id="colour_animation_wheel_stuck",
                fields={
                    "animated": len(animated),
                    "stuck": len(stuck),
                },
            )
        )
    return findings


def _animated_rgb_fixtures(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int
) -> set[int]:
    """The fixtures whose red, green or blue this look *animates*."""
    animated: set[int] = set()
    for member in graph.descendants(function_id):
        function = graph.functions.get(member)
        if function is None or not _animates_colour(function):
            continue
        for fixture_id, pairs in driven_channels(function, graph.capabilities, groups).items():
            capability = graph.capabilities.get(fixture_id)
            if capability is None:
                continue
            rgb = [
                offset
                for role in (roles.RED, roles.GREEN, roles.BLUE)
                for offset in capability.offsets_for_role(role)
            ]
            if any(offset in pairs for offset in rgb):
                animated.add(fixture_id)
    return animated


def _animates_colour(function: etree._Element) -> bool:
    """An EFX modulating red, green and blue - a hue that travels by itself.

    Matrices are deliberately out, on the same judgment `rule_wheel_colour`
    makes: a matrix paints the *pixels* of a group and can say nothing about a
    member that has none, so a two-colour Alternate over Cabezas is a claim
    about eight RGB heads and not about the four beams beside them. An EFX in
    RGB mode is the opposite - it names its fixtures one by one, and the ones
    it leaves out it leaves out silently.
    """
    if function.attrib.get("Type") != "EFX":
        return False
    # An EFX names its members `<Fixture>`, not `<EFXFixture>` - the class name
    # is EFXFixture but the tag is not (`efxfixture.cpp::saveXML`).
    for fixture in iter_local(function, "Fixture"):
        mode = find_local(fixture, "Mode")
        if mode is not None and (mode.text or "").strip() == EFX_RGB_MODE:
            return True
    return False


def _wheel_coloured(graph: ShowGraph, fixture_id: int) -> bool:
    capability = graph.capabilities.get(fixture_id)
    if capability is None:
        return False
    return capability.has_role(roles.COLOR_MACRO) and not capability.has_role(roles.RED)


def _is_lit(channels: dict[int, int | None]) -> bool:
    return any(lit(value) for value in channels.values())


def _wheel_animated(
    graph: ShowGraph, groups: dict[int, tuple[int, ...]], function_id: int, fixture_id: int
) -> bool:
    """Either a rotation range, or more than one detent across the look."""
    capability = graph.capabilities[fixture_id]
    offsets = set(capability.offsets_for_role(roles.COLOR_MACRO))
    seen: set[int] = set()
    for member in graph.descendants(function_id):
        function = graph.functions.get(member)
        if function is None:
            continue
        pairs = driven_channels(function, graph.capabilities, groups).get(fixture_id, {})
        for offset in offsets & set(pairs):
            value = pairs[offset]
            if value is None:  # an effect on the wheel itself: unpredictable, so moving
                return True
            if _in_rotation_range(capability, offset, value):
                return True
            seen.add(value)
    return len(seen) > 1


def _in_rotation_range(capability: FixtureCapabilities, offset: int, value: int) -> bool:
    for ranges in [capability.capabilities_by_offset[offset]]:
        for entry in ranges:
            if entry.minimum <= value <= entry.maximum and entry.preset.startswith(ROTATION):
                return True
    return False
