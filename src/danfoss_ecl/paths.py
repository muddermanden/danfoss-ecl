"""Configurable data directories (platformdirs / XDG)."""

from __future__ import annotations

import os
from pathlib import Path

from platformdirs import user_data_dir


APP_NAME = "danfoss-ecl"


def default_data_dir() -> Path:
    return Path(user_data_dir(APP_NAME, APP_NAME, roaming=False))


def default_dump_dir() -> Path:
    return default_data_dir() / "dumps"


def dump_dir() -> Path:
    override = os.getenv("ECL310_OUTPUT_DIR") or os.getenv("ECL310_DUMP_DIR")
    if override:
        return Path(override).expanduser()
    return default_dump_dir()
