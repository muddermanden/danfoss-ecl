"""Danfoss ECL Comfort Modbus helpers.

v0.1: A266.1 register map and a CLI dump tool.
Home Assistant is intentionally not a dependency yet.
"""

from danfoss_ecl.registers_a266 import REGISTERS, Register

__all__ = ["REGISTERS", "Register"]
__version__ = "0.1.0"
