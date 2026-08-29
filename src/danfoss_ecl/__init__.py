"""Danfoss ECL Comfort Modbus helpers.

v0.1: A266.1 register map and a CLI dump tool.
Home Assistant is intentionally not a dependency yet.
"""

from danfoss_ecl.decode import format_value, to_int16
from danfoss_ecl.i18n import gettext, setup_i18n
from danfoss_ecl.registers_a266 import REGISTERS, Register

__all__ = [
    "REGISTERS",
    "Register",
    "format_value",
    "gettext",
    "setup_i18n",
    "to_int16",
]
__version__ = "0.1.0"
