from __future__ import annotations

from collections.abc import Callable
from math import isclose

from danfoss_ecl.i18n import gettext as default_gettext
from danfoss_ecl.registers_a266 import Register, Variant

Translate = Callable[[str], str]
Engineering = int | float | str


def to_int16(value: int) -> int:
    return value - 65536 if value >= 32768 else value


def _tr(translate: Translate | None) -> Translate:
    return translate or default_gettext


def _scaled(raw: int, reg: Register) -> int | float:
    value = to_int16(raw) if reg.signed else raw
    return value if reg.scale == 1 else value / reg.scale


def format_number(value: int | float, scale: int) -> str:
    if scale == 1 and float(value).is_integer():
        return f"{int(value)}"
    if scale == 10:
        return f"{float(value):.1f}"
    if scale == 100:
        return f"{float(value):.2f}"
    if isinstance(value, float) and not value.is_integer():
        return f"{value:.1f}" if abs(value) < 100 else f"{value:.2f}"
    return f"{int(value)}" if float(value).is_integer() else f"{value}"


def engineering(raw: int, reg: Register, variant: Variant) -> Engineering:
    value = to_int16(raw) if reg.signed else raw
    if variant.choices is not None:
        if 0 <= value < len(variant.choices):
            return variant.choices[value]
        return value
    if reg.encoding == "majmin":
        return f"{value >> 8}.{value & 0xFF:02d}"
    if reg.encoding == "year_week":
        return f"{value & 0xFF}.{2000 + (value >> 8)}"
    if reg.encoding == "ascii":
        return chr(value) if 32 <= value <= 126 else str(value)
    scaled = _scaled(raw, reg)
    if variant.off is not None and scaled == variant.off:
        return "OFF"
    if reg.scale == 100 and isinstance(scaled, (int, float)) and scaled >= 180:
        return "open"
    return scaled


def format_value(
    raw: int,
    reg: Register,
    variant: Variant | None = None,
    *,
    translate: Translate | None = None,
) -> str:
    _ = _tr(translate)
    var = variant or reg.primary_variant()
    if var is None:
        return str(raw)
    current = engineering(raw, reg, var)
    if current == "OFF":
        return _("OFF")
    if current == "open":
        return _("open")
    if var.choices is not None and isinstance(current, str):
        return _(current)
    if isinstance(current, str):
        return current
    text = format_number(current, reg.scale)
    return f"{text} {var.unit}".strip()


def format_factory(
    reg: Register,
    variant: Variant | None,
    *,
    translate: Translate | None = None,
) -> str:
    _ = _tr(translate)
    if variant is None or variant.factory is None:
        return ""
    fac = variant.factory
    if fac == "OFF":
        return _("OFF")
    if variant.choices is not None and fac in variant.choices:
        return _(str(fac))
    if isinstance(fac, str):
        return _(fac) if fac in {"ON", "OFF"} else fac
    text = format_number(fac, reg.scale)
    return f"{text} {variant.unit}".strip()


def values_equal(left: Engineering, right: Engineering) -> bool:
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-9)
    return left == right


def deviation(
    raw: int,
    reg: Register,
    variant: Variant | None,
    *,
    translate: Translate | None = None,
) -> str:
    _ = _tr(translate)
    if variant is None:
        return _("not available")
    if variant.factory is None:
        return ""
    current = engineering(raw, reg, variant)
    if values_equal(current, variant.factory):
        return _("factory")
    return _("changed")


def range_text(
    reg: Register,
    variant: Variant | None = None,
    *,
    translate: Translate | None = None,
) -> str:
    _ = _tr(translate)
    var = variant or reg.primary_variant()
    if var is None:
        return ""
    if var.choices is not None:
        return " | ".join(_(choice) for choice in var.choices)
    parts: list[str] = []
    if var.off is not None:
        parts.append(_("OFF"))
    if var.vmin is not None and var.vmax is not None:
        parts.append(f"{var.vmin} … {var.vmax}")
    elif var.vmin is not None:
        parts.append(f"≥ {var.vmin}")
    elif var.vmax is not None:
        parts.append(f"≤ {var.vmax}")
    if var.unit:
        parts.append(var.unit)
    return " ".join(parts)


def in_range(
    raw: int,
    reg: Register,
    variant: Variant | None = None,
    *,
    translate: Translate | None = None,
) -> str:
    _ = _tr(translate)
    var = variant or reg.primary_variant()
    if var is None:
        return _("not available")
    current = engineering(raw, reg, var)
    if current in {"OFF", "open"}:
        return _("OFF") if current == "OFF" else _("open")
    if var.choices is not None:
        value = to_int16(raw) if reg.signed else raw
        return _("ok") if 0 <= value < len(var.choices) else _("out of range")
    if reg.encoding in {"majmin", "year_week", "ascii"}:
        return _("ok")
    if isinstance(current, (int, float)):
        if var.vmin is not None and current < var.vmin:
            return _("out of range")
        if var.vmax is not None and current > var.vmax:
            return _("out of range")
        if var.vmin is None and var.vmax is None:
            return ""
        return _("ok")
    return _("ok")
