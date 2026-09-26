"""2026-09-26, review of round D6: the offline copy drops the I/O patches and nothing else."""

from lxml import etree
from rig_root import RIG_ROOT

from qlctool.offline_workspace import offline_workspace
from qlctool.xmlutil import iter_local, localname

VIBRA = RIG_ROOT / "QLC+ Setups" / "Vibra.qxw"
IO = ("Input", "Output", "Feedback")


def _patches(root):
    """The I/O patches of the universes; a widget's <Input> binding is not one."""
    return [
        child
        for io_map in iter_local(root, "InputOutputMap")
        for universe in iter_local(io_map, "Universe")
        for child in universe
        if localname(child) in IO
    ]


def _without_io(root):
    for universe in iter_local(root, "Universe"):
        if localname(universe.getparent()) == "InputOutputMap":
            for child in [c for c in universe if localname(c) in IO]:
                universe.remove(child)
    return etree.tostring(root, method="c14n")


def test_the_copy_keeps_everything_but_the_io_patches(tmp_path):
    copy = offline_workspace(VIBRA, tmp_path / "copy.qxw")
    stripped = etree.parse(str(copy))
    assert _patches(etree.parse(str(VIBRA)).getroot()), "the frozen rig has patches to strip"
    assert not _patches(stripped.getroot())
    assert len(list(iter_local(stripped.getroot(), "Universe"))) >= 1
    assert stripped.docinfo.doctype == etree.parse(str(VIBRA)).docinfo.doctype
    assert etree.tostring(stripped.getroot(), method="c14n") == _without_io(
        etree.parse(str(VIBRA)).getroot()
    )


def test_a_universe_reference_elsewhere_is_left_alone(tmp_path):
    source = tmp_path / "show.qxw"
    source.write_text(
        '<Workspace xmlns="http://www.qlcplus.org/Workspace"><Engine>'
        '<InputOutputMap><Universe ID="0"><Output Plugin="DMX USB" Line="0"/></Universe>'
        "</InputOutputMap><Fixture><Universe>0</Universe><Channels>4</Channels></Fixture>"
        "</Engine></Workspace>"
    )
    root = etree.parse(str(offline_workspace(source, tmp_path / "copy.qxw"))).getroot()
    assert [u.text for u in iter_local(root, "Universe")] == [None, "0"]
    assert not list(iter_local(root, "Output"))


def test_the_microphone_beat_is_made_internal(tmp_path):
    """Vibra-beats' audio beat generator opened the microphone (2026-09-26)."""
    beats = RIG_ROOT / "QLC+ Setups" / "Vibra-beats.qxw"
    root = etree.parse(str(offline_workspace(beats, tmp_path / "c.qxw"))).getroot()
    assert [b.get("BeatType") for b in iter_local(root, "BeatGenerator")] == ["Internal"]


def test_a_network_server_never_starts_on_its_own(tmp_path):
    """A web server there would bind QLC+'s port, the operator's among them."""
    source = tmp_path / "show.qxw"
    source.write_text(
        '<Workspace xmlns="http://www.qlcplus.org/Workspace"><Engine><InputOutputMap>'
        '<BeatGenerator BeatType="Disabled" BPM="0"/>'
        '<NetworkServer Type="Web" AutoStart="True" Name="x" Password=""/>'
        "</InputOutputMap></Engine></Workspace>"
    )
    root = etree.parse(str(offline_workspace(source, tmp_path / "copy.qxw"))).getroot()
    server = next(iter_local(root, "NetworkServer"))
    assert (server.get("Type"), server.get("AutoStart")) == ("Web", "False")
    assert next(iter_local(root, "BeatGenerator")).get("BeatType") == "Disabled"
