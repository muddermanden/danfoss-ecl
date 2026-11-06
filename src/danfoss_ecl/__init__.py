"""Danfoss ECL Comfort Modbus helpers.

Device library first: A266 register catalog + decode + dump CLI.
Home Assistant is intentionally not a dependency yet.
"""

from danfoss_ecl.decode import deviation, format_value, to_int16
from danfoss_ecl.i18n import gettext, setup_i18n
from danfoss_ecl.registers_a266 import REGISTERS, Register, Variant

__all__ = [
    "REGISTERS",
    "Register",
    "Variant",
    "deviation",
    "format_value",
    "gettext",
    "setup_i18n",
    "to_int16",
]
__version__ = "0.1.0"
