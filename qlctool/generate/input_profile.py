"""The SMC-PAD input profile writer, kept at its published import path.

`tests/test_input_profile.py` here and in vibra-lighting import
`PROFILE_NAME` and `build_input_profile` from `qlctool.generate.input_profile`.
"""

from .build_input_profile import build_input_profile
from .input_profile_constants import PROFILE_NAME

__all__ = ["PROFILE_NAME", "build_input_profile"]
