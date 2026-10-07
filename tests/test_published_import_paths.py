"""The import paths other projects pin still hand back the very same objects."""

from qlctool import cli, main
from qlctool.generate import build_input_profile, input_profile, pad_channel, smc_pad_device


def test_cli_main_is_the_main_module_function() -> None:
    assert cli.main is main.main


def test_input_profile_reexports_its_writer_and_name() -> None:
    assert input_profile.build_input_profile is build_input_profile.build_input_profile
    assert input_profile.PROFILE_NAME == "M-VAVE SMC-PAD"


def test_smc_pad_device_reexports_the_pad_map() -> None:
    assert smc_pad_device.pad_channel is pad_channel.pad_channel
    assert smc_pad_device.pad_channel(1) == 36992 + 36
    assert smc_pad_device.PADS == 16
