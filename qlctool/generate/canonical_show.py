"""Build the whole show: content, structure, and a console that runs itself.

The shows this rig plays are unattended - the laptop is left alone and has to
keep changing colour, movement and gobos on its own - so the target is not a
console full of buttons for an operator, it is one AUTO function that brings up
everything at once, with the manual buttons there for when somebody does sit
down. The shape is taken from the hand-built show: colour banks per group with
Random wheels, mixed two-colour looks, gobo and prism animations, movement, and
smoke on a timer.
"""

from collections.abc import Sequence
from dataclasses import dataclass, field

from .. import roles
from ..capabilities_of import capabilities_of
from ..fixture_group import fixture_groups
from ..functions.collection import build_collection
from ..functions.scene import build_scene
from ..ids import next_function_id
from ..library import FixtureLibrary
from ..palette import PALETTE
from ..skeleton import strip_to_skeleton
from ..workspace import Workspace
from .color_banks import GeneratedBank, generate_color_banks
from .color_scene import color_scene_values
from .matrix_effects import generate_matrix_effects
from .movement_efx import generate_movement_efx
from .smoke_auto import generate_smoke_auto
from .vc_layout import generate_vc_layout
from .wheel_scenes import generate_wheel_scenes

SHOW_PATH = "Show"
MATRIX_ALGORITHMS: tuple[str | None, ...] = ("Fill", "Even/Odd", "Strobe", "Waves", None)
MATRIX_COLORS = ("Rojo", "Verde", "Azul", "Ambar", "Magenta", "Blanco")

# The console the owner works with: one key each, as the old show had them.
KEYS = {
    "AUTO": "Q",
    "Rueda Colores": "W",
    "Rueda Mezcla": "E",
    "Movimientos Cabezas": "A",
    "Gobo Animacion": "G",
    "Prisma Animacion": "P",
    "Humo Auto": "J",
    "Luces ON": "X",
    "Todo Blanco": "B",
    "Todo Negro": "º",
    "Flash 100%": "Space",
    "Flash 50%": "-",
}
FLASH_FUNCTIONS = ("Flash 100%", "Flash 50%")


@dataclass(frozen=True)
class CanonicalShow:
    banks: list[GeneratedBank] = field(default_factory=list)
    matrix_ids: list[int] = field(default_factory=list)
    efx_ids: list[int] = field(default_factory=list)
    gobo_ids: list[int] = field(default_factory=list)
    prism_ids: list[int] = field(default_factory=list)
    master_ids: dict[str, int] = field(default_factory=dict)
    button_ids: list[int] = field(default_factory=list)
    function_count: int = 0


def build_canonical_show(
    workspace: Workspace,
    library: FixtureLibrary,
    algorithms: Sequence[str | None] = MATRIX_ALGORITHMS,
    matrix_colors: Sequence[str] = MATRIX_COLORS,
    with_layout: bool = True,
) -> CanonicalShow:
    """Strip the workspace to its patch and generate a self-running show on it."""
    strip_to_skeleton(workspace)
    caps = capabilities_of(workspace.root, library)
    master: dict[str, int] = {}

    # Base looks first, so they are the lowest function IDs and read first.
    master["Luces ON"] = _flat_scene(workspace, caps, "Luces ON", (255, 255, 255))
    master["Todo Blanco"] = _flat_scene(
        workspace, caps, "Todo Blanco", PALETTE["Blanco"]
    )
    master["Todo Negro"] = _blackout(workspace, caps)
    master["Flash 100%"] = _flat_scene(
        workspace, caps, "Flash 100%", (255, 255, 255)
    )
    master["Flash 50%"] = _flat_scene(
        workspace, caps, "Flash 50%", (128, 128, 128)
    )

    banks = generate_color_banks(workspace, library)

    matrix_ids: list[int] = []
    matrix_chasers: list[int] = []
    subset = {name: PALETTE[name] for name in matrix_colors}
    for group in fixture_groups(workspace.root):
        matrices = generate_matrix_effects(
            workspace,
            group_id=group.group_id,
            algorithms=algorithms,
            palette=subset,
            path=f"Matrices {group.name}",
        )
        matrix_ids.extend(matrices.matrix_ids)
        if matrices.chaser_id is not None:
            matrix_chasers.append(matrices.chaser_id)

    movement = generate_movement_efx(
        workspace, library, path="Movimiento", chaser_hold=10000,
        chaser_run_order="Random",
    )
    if movement.chaser_id is not None:
        master["Movimientos Cabezas"] = movement.chaser_id

    gobos = generate_wheel_scenes(
        workspace, library, role=roles.GOBO, label="Gobo", path="Gobos"
    )
    if gobos.chaser_id is not None:
        master["Gobo Animacion"] = gobos.chaser_id
    prisms = generate_wheel_scenes(
        workspace, library, role=roles.PRISM, label="Prisma", run_order="Loop",
        hold=8000, path="Prisma",
    )
    if prisms.chaser_id is not None:
        master["Prisma Animacion"] = prisms.chaser_id

    smoke = generate_smoke_auto(workspace, library)
    master["Humo Auto"] = smoke.chaser_id

    master["Rueda Colores"] = _collection(
        workspace, "Rueda Colores",
        [b.wheel_id for b in banks if b.wheel_id is not None],
    )
    master["Rueda Mezcla"] = _collection(
        workspace, "Rueda Mezcla",
        [b.mix_wheel_id for b in banks if b.mix_wheel_id is not None],
    )
    # The one thing to press: colour, movement, gobos, matrices and haze at once.
    master["AUTO"] = _collection(
        workspace, "AUTO",
        [master["Rueda Colores"], master["Movimientos Cabezas"],
         master["Gobo Animacion"], master["Humo Auto"], *matrix_chasers],
    )

    button_ids: list[int] = []
    if with_layout:
        button_ids = _lay_out_console(workspace, master)

    functions = [
        f for f in workspace.engine if f.tag.endswith("}Function")
    ]
    return CanonicalShow(
        banks=banks,
        matrix_ids=matrix_ids,
        efx_ids=movement.efx_ids,
        gobo_ids=gobos.scene_ids,
        prism_ids=prisms.scene_ids,
        master_ids=master,
        button_ids=button_ids,
        function_count=len(functions),
    )


def _flat_scene(workspace, caps, name, rgb) -> int:
    """One colour on every colour-capable fixture; smoke machines excluded."""
    values = color_scene_values(caps, rgb)
    function_id = next_function_id(workspace.root)
    workspace.add_function(
        build_scene(function_id, name, values, path=SHOW_PATH)
    )
    return function_id


def _blackout(workspace, caps) -> int:
    """Everything to zero - except the smoke machine, which is never touched."""
    values: dict[int, list[tuple[int, int]]] = {}
    for capability in caps:
        if capability.is_smoke:
            continue
        offsets = [
            offset
            for role in (roles.RED, roles.GREEN, roles.BLUE, roles.WHITE, roles.DIMMER)
            for offset in capability.offsets_for_role(role)
        ]
        if offsets:
            values[capability.fixture.fixture_id] = [(o, 0) for o in sorted(offsets)]
    function_id = next_function_id(workspace.root)
    workspace.add_function(
        build_scene(function_id, "Todo Negro", values, path=SHOW_PATH)
    )
    return function_id


def _collection(workspace: Workspace, name: str, members: list[int]) -> int:
    function_id = next_function_id(workspace.root)
    workspace.add_function(
        build_collection(function_id, name, members, path=SHOW_PATH)
    )
    return function_id


def _lay_out_console(workspace: Workspace, master: dict[str, int]) -> list[int]:
    """The master frame first, at the top, then a frame per generated folder."""
    keys = {
        master[name]: key for name, key in KEYS.items() if name in master
    }
    actions = {
        master[name]: "Flash" for name in FLASH_FUNCTIONS if name in master
    }
    top = generate_vc_layout(
        workspace,
        function_ids=list(master.values()),
        columns=6,
        keys=keys,
        actions=actions,
    )
    rest = generate_vc_layout(workspace, columns=10)
    return top.button_ids + rest.button_ids
