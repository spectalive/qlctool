"""2026-09-27, Round 2 review: `stage_ordered` and `alternate_mirror` on their own.

Only the Vibra outcome was asserted; these are the edges - a lone head, two
heads on one side, no Monitor at all, a rigged head the plot never placed.
"""

from lxml import etree

from qlctool.generate.alternate_mirror import alternate_mirror
from qlctool.stage_ordered import stage_ordered

NS = "http://www.qlcplus.org/Workspace"


def _root(patched, placed=None, hidden=()):
    """A workspace patching `patched`, with a Monitor placing `placed` (id -> x) if given."""
    root = etree.Element(f"{{{NS}}}Workspace")
    engine = etree.SubElement(root, f"{{{NS}}}Engine")
    for fixture_id in patched:
        fixture = etree.SubElement(engine, f"{{{NS}}}Fixture")
        etree.SubElement(fixture, f"{{{NS}}}ID").text = str(fixture_id)
        etree.SubElement(fixture, f"{{{NS}}}Channels").text = "1"
    if placed is not None:
        monitor = etree.SubElement(engine, f"{{{NS}}}Monitor")
        for fixture_id, x in placed.items():
            item = etree.SubElement(monitor, f"{{{NS}}}FxItem", ID=str(fixture_id), XPos=str(x))
            if fixture_id in hidden:
                item.set("Hidden", "1")
    return root


def test_rigged_heads_go_left_to_right_then_unplaced_then_spares():
    root = _root([1, 2, 3, 4, 5], placed={1: 900, 2: 100, 3: 500, 4: 300}, hidden={4})
    # 5 is rigged but the plot never placed it; 4 is a spare.
    assert stage_ordered(root, [1, 2, 3, 4, 5]) == [2, 3, 1, 5, 4]
    assert stage_ordered(root, [5, 4, 3]) == [3, 5, 4]


def test_no_monitor_keeps_the_given_order():
    root = _root([3, 1, 2])
    assert stage_ordered(root, [3, 1, 2]) == [3, 1, 2]


def test_a_lone_head_the_default_runs_forward_is_reversed():
    assert alternate_mirror([5], []) == {5}
    assert alternate_mirror([5], [5]) == set()


def test_two_heads_either_side_both_run_forward():
    # Every other head is the house-right one: ruling D5, both forward.
    assert alternate_mirror([1, 2], [2]) == set()


def test_two_heads_on_one_side_reverse_one():
    assert alternate_mirror([1, 2], []) == {2}
    assert alternate_mirror([1, 2], [1, 2]) == {2}


def test_every_other_across_the_stage():
    # Vibra's 7R across the stage; the default reverses the house-right pair.
    assert alternate_mirror([20, 22, 23, 21], [23, 21]) == {22, 21}
    # No Monitor: no sides, so no default mirror.
    assert alternate_mirror([20, 22, 23, 21], []) == {22, 21}
