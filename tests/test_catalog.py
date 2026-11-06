from danfoss_ecl.decode import deviation, format_factory, format_value
from danfoss_ecl.i18n import gettext, setup_i18n
from danfoss_ecl.registers_a266 import REGISTERS


def setup_module() -> None:
    setup_i18n("en")


def _by_pnu(pnu: int):
    return next(reg for reg in REGISTERS if reg.pnu == pnu)


def test_every_register_has_a_variant():
    assert all(reg.variants for reg in REGISTERS)


def test_unique_pnus():
    pnus = [reg.pnu for reg in REGISTERS]
    assert len(pnus) == len(set(pnus))


def test_nz_factory_and_changed():
    setup_i18n("en")
    reg = _by_pnu(11187)
    var = reg.variant_for("1")
    assert var is not None
    assert var.factory == 3
    assert format_value(3, reg, var) == "3 K"
    assert deviation(3, reg, var) == "factory"
    assert format_value(1, reg, var) == "1 K"
    assert deviation(1, reg, var) == "changed"
    assert format_factory(reg, var) == "3 K"


def test_m_run_heating_vs_dhw_factory():
    heat = _by_pnu(11186).variant_for("1")
    dhw = _by_pnu(12186).variant_for("1")
    assert heat is not None and dhw is not None
    assert heat.factory == 60
    assert dhw.factory == 20
    assert _by_pnu(12186).variant_for("9").factory == 15


def test_adapt_time_double_hyphen_factory():
    reg = _by_pnu(11015)
    assert reg.variant_for("1").factory == "OFF"
    assert reg.variant_for("9").factory == 25
    assert format_value(0, reg, reg.variant_for("1")) == "OFF"


def test_max_flow_t_not_on_a266_1():
    assert _by_pnu(11079).variant_for("1") is None
    assert _by_pnu(11079).variant_for("2") is not None


def test_input_type_range_differs_on_9():
    reg = _by_pnu(11109)
    v1 = reg.variant_for("1")
    v9 = reg.variant_for("9")
    assert v1 is not None and v9 is not None
    assert v1.choices is not None and "IM1" in v1.choices
    assert v9.choices is not None and "IM1" not in v9.choices


def test_s3_circuit_view_unavailable():
    assert _by_pnu(11203).variant_for("1") is None


def test_poll_groups():
    assert _by_pnu(10201).poll_group == "fast"
    assert _by_pnu(11187).poll_group == "slow"
    assert _by_pnu(35).poll_group == "once"
    assert _by_pnu(4006).poll_group == "fast"


def test_appendix_names():
    assert _by_pnu(11186).name == "M run"
    assert _by_pnu(11187).name == "Nz"
    assert _by_pnu(11174).name == "Motor pr."


def test_danish_register_name():
    setup_i18n("da")
    assert gettext("Sensors") == "Føler"
    assert gettext("M run") == "M-gang"
    assert gettext("Nz") == "Nz"
    assert gettext("changed") == "ændret"
    assert gettext("factory") == "fabrik"
    setup_i18n("en")
