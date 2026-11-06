from danfoss_ecl.decode import deviation, format_factory, format_value, to_int16
from danfoss_ecl.i18n import gettext, setup_i18n
from danfoss_ecl.registers_a266 import REGISTERS, Register, V


def setup_module() -> None:
    setup_i18n("en")


def _by_pnu(pnu: int) -> Register:
    return next(reg for reg in REGISTERS if reg.pnu == pnu)


def test_int16_negative():
    assert to_int16(65521) == -15


def test_scale_100_sensor():
    reg = _by_pnu(10201)
    assert format_value(1794, reg, reg.variant_for("1")) == "17.94 °C"


def test_open_sensor_en():
    setup_i18n("en")
    reg = _by_pnu(10202)
    assert format_value(19200, reg, reg.variant_for("1")) == "open"


def test_open_sensor_da():
    setup_i18n("da")
    reg = _by_pnu(10202)
    assert format_value(19200, reg, reg.variant_for("1")) == "åben"
    setup_i18n("en")


def test_off_nine():
    reg = _by_pnu(11174)
    assert format_value(9, reg, reg.variant_for("1")) == "OFF"


def test_enum():
    reg = _by_pnu(11024)
    assert format_value(1, reg, reg.variant_for("1")) == "GEAR"


def test_setpoint_scale_10():
    reg = _by_pnu(12190)
    assert format_value(530, reg, reg.variant_for("1")) == "53.0 °C"


def test_software_version_majmin():
    reg = _by_pnu(35)
    assert format_value(557, reg) == "2.45"
    assert format_value(257, reg) == "1.01"


def test_hardware_revision_majmin():
    reg = _by_pnu(34)
    assert format_value(18692, reg) == "73.04"
    assert format_value(16642, reg) == "65.02"


def test_production_week_year():
    reg = _by_pnu(2099)
    assert format_value(2563, reg) == "3.2010"
    assert format_value(25 * 256 + 32, reg) == "32.2025"


def test_application_prefix_ascii():
    reg = _by_pnu(2060)
    assert format_value(65, reg) == "A"
