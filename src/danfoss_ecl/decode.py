from __future__ import annotations

from collections.abc import Callable

from danfoss_ecl.i18n import gettext as default_gettext
from danfoss_ecl.registers_a266 import Register

Translate = Callable[[str], str]


def to_int16(value: int) -> int:
    return value - 65536 if value >= 32768 else value


def format_value(raw: int, reg: Register, *, translate: Translate | None = None) -> str:
    _ = translate or default_gettext
    value = to_int16(raw) if reg.signed else raw

    if reg.choices is not None:
        if 0 <= value < len(reg.choices):
            return _(reg.choices[value])
        return f"? ({value})"

    scaled = value if reg.scale == 1 else value / reg.scale

    if reg.off is not None and scaled == reg.off:
        return _("OFF")

    if reg.scale == 100 and scaled >= 180:
        return _("open")

    if reg.scale == 1:
        text = f"{int(scaled)}"
    elif reg.scale == 10:
        text = f"{scaled:.1f}"
    else:
        text = f"{scaled:.2f}"
    return f"{text} {reg.unit}".strip()


def range_text(reg: Register, *, translate: Translate | None = None) -> str:
    _ = translate or default_gettext
    if reg.choices is not None:
        return " | ".join(_(choice) for choice in reg.choices)
    parts: list[str] = []
    if reg.off is not None:
        parts.append(_("OFF"))
    if reg.vmin is not None and reg.vmax is not None:
        parts.append(f"{reg.vmin} … {reg.vmax}")
    elif reg.vmin is not None:
        parts.append(f"≥ {reg.vmin}")
    elif reg.vmax is not None:
        parts.append(f"≤ {reg.vmax}")
    if reg.unit:
        parts.append(reg.unit)
    return " ".join(parts)


def in_range(raw: int, reg: Register, *, translate: Translate | None = None) -> str:
    _ = translate or default_gettext
    value = to_int16(raw) if reg.signed else raw
    if reg.choices is not None:
        return _("ok") if 0 <= value < len(reg.choices) else _("out of range")
    scaled = value if reg.scale == 1 else value / reg.scale
    if reg.off is not None and scaled == reg.off:
        return _("OFF")
    if reg.scale == 100 and scaled >= 180:
        return _("open")
    if reg.vmin is not None and scaled < reg.vmin:
        return _("out of range")
    if reg.vmax is not None and scaled > reg.vmax:
        return _("out of range")
    if reg.vmin is None and reg.vmax is None:
        return ""
    return _("ok")
