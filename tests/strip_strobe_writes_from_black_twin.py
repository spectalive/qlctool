"""Make a Todo Negro twin model the old Intensity-only black step."""

from fixture_val_pairs import fixture_val_pairs as _pairs_of
from write_fixture_val_pairs import write_fixture_val_pairs as _write_pairs

from qlctool import roles
from qlctool.findall_local import findall_local


def strip_strobe_writes_from_black_twin(black, capabilities):
    """Make a Todo Negro twin model the old Intensity-only black step."""
    for value in list(findall_local(black, "FixtureVal")):
        fixture_id = int(value.attrib["ID"])
        capability = capabilities.get(fixture_id)
        assert capability is not None, f"black twin fixture {fixture_id} has no capability"
        pairs = _pairs_of(value)
        for offset in capability.offsets_for_role(roles.STROBE):
            pairs.pop(offset, None)
        if pairs:
            _write_pairs(value, pairs)
        else:
            value.getparent().remove(value)

    intensity_writes = 0
    for value in findall_local(black, "FixtureVal"):
        fixture_id = int(value.attrib["ID"])
        capability = capabilities[fixture_id]
        for offset, level in _pairs_of(value).items():
            assert capability.roles_by_offset[offset] != roles.STROBE, (
                f"black twin still writes a shutter/strobe on fixture {fixture_id}"
            )
            if capability.groups_by_offset[offset] == "Intensity":
                assert level == 0, (
                    f"black twin writes lit Intensity channel {offset} on fixture {fixture_id}"
                )
                intensity_writes += 1
    assert intensity_writes, "black twin lost every zero-valued Intensity darkness claim"
