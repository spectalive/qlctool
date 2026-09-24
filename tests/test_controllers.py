"""Controllers are optional profiles; their checks run only where they apply (2026-09-24).

Spec step 4: "A show without a controller block gets neither, and its checks do
not run", and `qlctool check` still runs every check that applies, found
through the `qlctool.rules` entry points.
"""

from dataclasses import replace
from pathlib import Path

import pytest

from qlctool.checks.finding import ERROR, Finding
from qlctool.checks.pad_bindings import pad_bindings
from qlctool.checks.rule_provider import RuleProvider
from qlctool.checks.rule_providers import rule_providers
from qlctool.checks.run import check_workspace
from qlctool.description.controller_settings import ControllerSettings
from qlctool.desk_function_path import DESK_FUNCTION_PATH
from qlctool.generate.canonical_show import build_canonical_show
from qlctool.library import FixtureLibrary
from qlctool.vibra.description import vibra_description
from qlctool.workspace import Workspace

SHOW = Path(__file__).resolve().parents[3] / "QLC+ Setups" / "Vibra.qxw"


@pytest.fixture(scope="module")
def library():
    return FixtureLibrary.load()


@pytest.fixture(scope="module")
def bare(library):
    workspace = Workspace.load(SHOW)
    description = replace(vibra_description(), controllers=ControllerSettings())
    build_canonical_show(workspace, library, description=description)
    return workspace


def test_the_toolkits_own_providers_are_registered():
    assert {p.name for p in rule_providers()} >= {"smc-pad", "tablet_desk"}


def test_the_vibra_show_uses_both_controllers():
    root = Workspace.load(SHOW).root
    providers = {p.name: p for p in rule_providers()}
    assert providers["smc-pad"].applies(root)
    assert providers["tablet_desk"].applies(root)


def test_a_provider_runs_only_where_it_applies(library):
    workspace = Workspace.load(SHOW)
    seen = []

    def check(context):
        seen.append(context.root)
        return [Finding("regla de prueba", ERROR, "x", "y")]

    quiet = RuleProvider("quiet", applies=lambda root: False, check=check)
    loud = RuleProvider("loud", applies=lambda root: True, check=check)
    assert check_workspace(workspace, library, providers=[quiet]) == []
    assert [f.rule for f in check_workspace(workspace, library, providers=[loud])] == [
        "regla de prueba"
    ]
    assert len(seen) == 1


def test_a_show_without_controllers_has_no_pad_binding_and_no_desk(bare):
    assert not pad_bindings(bare.root)
    assert not any(f.get("Path") == DESK_FUNCTION_PATH for f in bare.engine)
    own = [p for p in rule_providers() if p.name in ("smc-pad", "tablet_desk")]
    assert not any(p.applies(bare.root) for p in own)


def test_a_show_without_controllers_passes_every_check(bare, library):
    assert check_workspace(bare, library) == []


def test_an_unknown_pad_is_refused(library):
    description = replace(vibra_description(), controllers=ControllerSettings(midi_pad="launchpad"))
    with pytest.raises(ValueError, match="smc-pad"):
        build_canonical_show(Workspace.load(SHOW), library, description=description)
