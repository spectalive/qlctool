"""The surfaces the Vibra show is played from: the SMC-PAD and the tablet desk."""

from ..description.controller_settings import ControllerSettings

VIBRA_CONTROLLERS = ControllerSettings(midi_pad="smc-pad", tablet_desk=True)
