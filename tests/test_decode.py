from danfoss_ecl.dump import format_value, to_int16
from danfoss_ecl.registers_a266 import Register


def test_int16_negative():
    assert to_int16(65521) == -15


def test_scale_100_sensor():
    reg = Register("Føler", "S1", 10201, 100, "°C", True, -60, 150)
    assert format_value(1794, reg) == "17.94 °C"


def test_open_sensor():
    reg = Register("Føler", "S2", 10202, 100, "°C", True, -60, 150)
    assert format_value(19200, reg) == "åben"


def test_off_nine():
    reg = Register("Varme", "Motorbeskyttelse", 11174, unit="min", vmin=10, vmax=59, off=9)
    assert format_value(9, reg) == "OFF"


def test_enum():
    reg = Register("Varme", "Motortype", 11024, choices=("ABV", "GEAR"))
    assert format_value(1, reg) == "GEAR"


def test_setpoint_scale_10():
    reg = Register("VV", "Ønsket VV komfort", 12190, 10, "°C", True, 10.0, 110.0)
    assert format_value(530, reg) == "53.0 °C"
