"""Write the workspace's rig as an MVR package with its GDTF files inside.

One layer, one fixture per patched fixture the `<Monitor>` node places and does
not hide, each pointing at the GDTF of its definition by file name and carrying
its mode, its universe and address, and its matrix. Spares - patched but hidden
- stay out, as they do in QLC+'s own views; a fixture whose definition the
library does not know is reported, not guessed.

Fixture UUIDs are derived from the fixture ID, so re-importing a regenerated
package updates the fixtures BlenderDMX already has instead of doubling them.
"""

import tempfile
import uuid
from pathlib import Path

import pymvr

from ..fixture import patched_fixtures
from ..library import FixtureLibrary
from ..workspace import Workspace
from .gdtf_file_name import gdtf_file_name
from .gdtf_name import gdtf_name
from .monitor_items import monitor_items
from .mvr_export import MvrExport
from .mvr_matrix import mvr_matrix
from .write_gdtf import write_gdtf

NAMESPACE = uuid.UUID("2b9d3f6a-0c4e-4b1f-8f6d-1e5a7c9b3d20")
LAYER_NAME = "Rig"


def write_mvr(
    workspace: Workspace,
    library: FixtureLibrary,
    out: Path,
    gobo_dir: Path | None,
) -> MvrExport:
    placed = monitor_items(workspace.root)
    if placed is None:
        raise ValueError("the workspace has no Monitor node: run `qlctool stage` first")
    items = {item.fixture_id: item for item in placed.items}

    export = MvrExport(path=out)
    layer = pymvr.Layer(name=LAYER_NAME, child_list=pymvr.ChildList())
    scene = pymvr.Scene(layers=pymvr.Layers([layer]))

    with tempfile.TemporaryDirectory(prefix="qlctool-gdtf-") as scratch:
        written: dict[str, Path] = {}
        for fixture in patched_fixtures(workspace.root):
            definition = library.get(fixture.manufacturer, fixture.model)
            item = items.get(fixture.fixture_id)
            label = f"{fixture.name} [{fixture.fixture_id}]"
            if definition is None:
                export.skipped[label] = "no definition in the library"
                continue
            if item is None or item.hidden:
                export.skipped[label] = "not placed" if item is None else "hidden spare"
                continue
            if fixture.mode not in definition.modes:
                export.skipped[label] = f"mode {fixture.mode!r} not in the definition"
                continue

            name = gdtf_file_name(definition)
            if name not in written:
                written[name] = write_gdtf(definition, Path(scratch), gobo_dir)
                export.gdtf_files.append(name)

            layer.child_list.fixtures.append(
                pymvr.Fixture(
                    name=fixture.name,
                    uuid=str(uuid.uuid5(NAMESPACE, str(fixture.fixture_id))),
                    gdtf_spec=name,
                    gdtf_mode=gdtf_name(fixture.mode),
                    fixture_id=str(fixture.fixture_id),
                    fixture_id_numeric=fixture.fixture_id,
                    unit_number=fixture.fixture_id,
                    matrix=mvr_matrix(item, definition, placed.stage),
                    addresses=pymvr.Addresses(
                        addresses=[
                            pymvr.Address(
                                dmx_break=1,
                                universe=fixture.universe + 1,
                                address=fixture.address + 1,
                            )
                        ]
                    ),
                )
            )
            export.fixtures.append(fixture.name)

        writer = pymvr.GeneralSceneDescriptionWriter()
        writer.serialize_scene(scene)
        writer.files_list = [(str(path), name) for name, path in written.items()]
        out.parent.mkdir(parents=True, exist_ok=True)
        writer.write_mvr(str(out))
    return export
