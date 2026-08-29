from danfoss_ecl.decode import format_value, to_int16
from danfoss_ecl.i18n import setup_i18n, gettext
from danfoss_ecl.registers_a266 import Register


def setup_module() -> None:
    setup_i18n("en")


def test_int16_negative():
    assert to_int16(65521) == -15


def test_scale_100_sensor():
    reg = Register("Sensors", "S1 outdoor raw", 10201, 100, "°C", True, -60, 150)
    assert format_value(1794, reg) == "17.94 °C"


def test_open_sensor_en():
    setup_i18n("en")
    reg = Register("Sensors", "S2 room raw", 10202, 100, "°C", True, -60, 150)
    assert format_value(19200, reg) == "open"


def test_open_sensor_da():
    setup_i18n("da")
    reg = Register("Sensors", "S2 room raw", 10202, 100, "°C", True, -60, 150)
    assert format_value(19200, reg) == "åben"
    setup_i18n("en")


def test_off_nine():
    reg = Register("Heating", "Motor protection", 11174, unit="min", vmin=10, vmax=59, off=9)
    assert format_value(9, reg) == "OFF"


def test_enum():
    reg = Register("Heating", "Actuator type", 11024, choices=("ABV", "GEAR"))
    assert format_value(1, reg) == "GEAR"


def test_setpoint_scale_10():
    reg = Register("DHW", "Desired DHW comfort", 12190, 10, "°C", True, 10.0, 110.0)
    assert format_value(530, reg) == "53.0 °C"


def test_danish_register_name():
    setup_i18n("da")
    assert gettext("Sensors") == "Føler"
    assert gettext("Motor running time") == "Motor-køretid"
    setup_i18n("en")
