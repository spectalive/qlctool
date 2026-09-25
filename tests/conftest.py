"""Suite-wide set-up: the fixture library reads the test rig's definitions.

`FixtureLibrary.load()` resolves its folders from QLCTOOL_FIXTURES or the
nearest qlctool.toml above the current directory; pytest can be started from
anywhere, so the suite names the rig's folder explicitly unless the caller did.
"""

import os

from rig_root import RIG_ROOT

os.environ.setdefault("QLCTOOL_FIXTURES", str(RIG_ROOT / "QLC+ Fixtures"))
