from __future__ import annotations

import argparse
import csv
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pymodbus.client import ModbusSerialClient, ModbusTcpClient
from pymodbus.exceptions import ModbusException

from danfoss_ecl.decode import (
    deviation,
    format_factory,
    format_value,
    in_range,
    range_text,
)
from danfoss_ecl.i18n import _, setup_i18n
from danfoss_ecl.paths import dump_dir
from danfoss_ecl.registers_a266 import REGISTERS, Register, Variant


Mode = Literal["tcp", "rtu"]


@dataclass(frozen=True)
class ModbusSettings:
    mode: Mode
    unit_id: int
    host: str
    port: int
    serial_port: str
    baudrate: int
    parity: str
    stopbits: int
    bytesize: int
    lang: str
    output_dir: Path
    app: str


def env_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None or raw_value == "":
        return default
    return int(raw_value)


ENV_FILE_NAMES = ("ecl310_a266.env", ".env")


class SettingsError(ValueError):
    """Configuration is missing or invalid."""


def load_env_files(env_file: Path | None = None, cwd: Path | None = None) -> list[Path]:
    """Load settings files into os.environ and return the files that were loaded.

    Real environment variables always win (python-dotenv never overrides them).
    With ``env_file`` only that file is loaded and it must exist. Without it,
    ``ecl310_a266.env`` and then ``.env`` are loaded from the current folder.
    """
    if env_file is not None:
        path = env_file.expanduser()
        if not path.is_file():
            raise SettingsError(f"Settings file not found: {path}")
        load_dotenv(path)
        return [path]
    base = cwd or Path.cwd()
    loaded: list[Path] = []
    for name in ENV_FILE_NAMES:
        path = base / name
        if path.is_file():
            load_dotenv(path)
            loaded.append(path)
    return loaded


def load_settings(host: str | None = None) -> ModbusSettings:
    """Build settings from the environment. Call load_env_files() first."""
    mode = os.getenv("ECL310_MODBUS_MODE", "tcp").lower()
    if mode not in {"tcp", "rtu"}:
        raise SettingsError("ECL310_MODBUS_MODE must be either 'tcp' or 'rtu'")

    resolved_host = host or os.getenv("ECL310_HOST", "")
    if mode == "tcp" and not resolved_host:
        raise SettingsError(
            "No controller address: set ECL310_HOST in ecl310_a266.env "
            "(copy ecl310_a266.env.example) or pass --host."
        )

    lang = setup_i18n()
    return ModbusSettings(
        mode=mode,  # type: ignore[arg-type]
        unit_id=env_int("ECL310_UNIT_ID", 1),
        host=resolved_host,
        port=env_int("ECL310_PORT", 502),
        serial_port=os.getenv("ECL310_SERIAL_PORT", "/dev/tty.usbserial-0001"),
        baudrate=env_int("ECL310_BAUDRATE", 38400),
        parity=os.getenv("ECL310_PARITY", "N"),
        stopbits=env_int("ECL310_STOPBITS", 1),
        bytesize=env_int("ECL310_BYTESIZE", 8),
        lang=lang,
        output_dir=dump_dir(),
        app=os.getenv("ECL310_APP", "1"),
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ecl-dump",
        description="Read-only dump of Danfoss ECL Comfort 310 A266 holding registers to CSV.",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        help="settings file to load instead of ./ecl310_a266.env and ./.env",
    )
    parser.add_argument("--host", help="controller IP or hostname (overrides ECL310_HOST)")
    return parser.parse_args(argv)


def build_client(settings: ModbusSettings) -> ModbusTcpClient | ModbusSerialClient:
    if settings.mode == "tcp":
        return ModbusTcpClient(host=settings.host, port=settings.port, timeout=5)
    return ModbusSerialClient(
        port=settings.serial_port,
        baudrate=settings.baudrate,
        parity=settings.parity,
        stopbits=settings.stopbits,
        bytesize=settings.bytesize,
        timeout=3,
    )


def read_holding(client: ModbusTcpClient | ModbusSerialClient, pnu: int, unit_id: int) -> int:
    address = pnu - 1
    attempts = (
        {"address": address, "count": 1, "slave": unit_id},
        {"address": address, "count": 1, "device_id": unit_id},
    )
    last_error: Exception | None = None
    for kwargs in attempts:
        try:
            result = client.read_holding_registers(**kwargs)
            if result.isError():
                last_error = RuntimeError(str(result))
                continue
            return int(result.registers[0])
        except TypeError as exc:
            last_error = exc
            continue
        except (ModbusException, ConnectionError, AttributeError) as exc:
            last_error = exc
            continue
    raise RuntimeError(str(last_error))


def _row(
    *,
    group: str,
    name: str,
    title: str,
    kind: str,
    pnu: int,
    raw: str | int,
    scale: int | str,
    encoding: str,
    value: str,
    unit: str,
    factory: str,
    deviation_text: str,
    range_s: str,
    a266: str,
    page: str,
    status: str,
    description: str,
    columns: dict[str, str],
) -> dict[str, str | int]:
    return {
        columns["group"]: group,
        columns["name"]: name,
        columns["title"]: title,
        columns["kind"]: kind,
        "pnu": pnu,
        "addr": pnu - 1,
        "raw": raw,
        columns["scale"]: scale,
        columns["encoding"]: encoding,
        columns["value"]: value,
        columns["unit"]: unit,
        columns["factory"]: factory,
        columns["deviation"]: deviation_text,
        columns["range"]: range_s,
        "a266": a266,
        columns["page"]: page,
        columns["status"]: status,
        columns["description"]: description,
    }


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    try:
        loaded = load_env_files(args.env_file)
        settings = load_settings(host=args.host)
    except SettingsError as exc:
        sys.exit(f"ecl-dump: {exc}")
    if loaded:
        print(_("Settings: {files}").format(files=", ".join(str(path) for path in loaded)))
    else:
        print(_("Settings: no settings file found, using environment variables only"))
    client = build_client(settings)
    if not client.connect():
        raise ConnectionError(
            _("Could not connect to {host}:{port}").format(
                host=settings.host, port=settings.port
            )
        )

    settings.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_path = settings.output_dir / f"ecl310_a266_dump_{stamp}.csv"
    rows: list[dict[str, str | int]] = []
    app = settings.app

    columns = {
        "group": _("group"),
        "name": _("name"),
        "title": _("title"),
        "kind": _("kind"),
        "scale": _("scale"),
        "encoding": _("encoding"),
        "value": _("value"),
        "unit": _("unit"),
        "factory": _("factory"),
        "deviation": _("deviation"),
        "range": _("range"),
        "page": _("page"),
        "status": _("status"),
        "description": _("description"),
    }

    print(
        f"ECL 310 A266.{app}  {settings.host}:{settings.port}  "
        f"{_('unit')} {settings.unit_id}  "
        f"{_('{count} PNUs').format(count=len(REGISTERS))}  [{settings.lang}]\n"
    )
    current_group = ""
    ok = 0
    fail = 0
    changed = 0

    def emit(
        reg: Register,
        variant: Variant | None,
        *,
        raw: str | int,
        value: str,
        status: str,
        deviation_text: str,
        description: str = "",
    ) -> None:
        factory = format_factory(reg, variant) if variant else ""
        range_s = range_text(reg, variant)
        unit = variant.unit if variant else ""
        a266 = variant.a266_text() if variant else ""
        page = "" if reg.guide_page is None else str(reg.guide_page)
        rows.append(
            _row(
                group=_(reg.group),
                name=_(reg.name),
                title=_(reg.title) if reg.title else "",
                kind=_(reg.kind),
                pnu=reg.pnu,
                raw=raw,
                scale=reg.scale,
                encoding=reg.encoding,
                value=value,
                unit=unit,
                factory=factory,
                deviation_text=deviation_text,
                range_s=range_s,
                a266=a266,
                page=page,
                status=status,
                description=_(description) if description else (_(reg.description) if reg.description else ""),
                columns=columns,
            )
        )

    try:
        for reg in REGISTERS:
            group = _(reg.group)
            name = _(reg.name)
            if reg.group != current_group:
                current_group = reg.group
                print(f"\n=== {group} ===")
            variant = reg.variant_for(app)
            if variant is None:
                status = _("not available")
                value = _("n/a")
                print(f"  {reg.pnu:5d}  {name:<24} {value:<16} {status}")
                emit(reg, None, raw="", value=value, status=status, deviation_text=status)
                continue
            try:
                raw = read_holding(client, reg.pnu, settings.unit_id)
                value = format_value(raw, reg, variant)
                status = in_range(raw, reg, variant)
                dev = deviation(raw, reg, variant)
                mark = "*" if dev == _("changed") else " "
                extra = f"  {_('factory')} {format_factory(reg, variant)}" if dev == _("changed") else ""
                print(
                    f" {mark}{reg.pnu:5d}  {name:<24} {value:<16} "
                    f"{(dev or status):<12}  {range_text(reg, variant)}{extra}"
                )
                if dev == _("changed") and reg.description:
                    print(f"         {_(reg.description)}")
                emit(
                    reg,
                    variant,
                    raw=raw,
                    value=value,
                    status=status,
                    deviation_text=dev,
                )
                ok += 1
                if dev == _("changed"):
                    changed += 1
            except Exception as exc:  # noqa: BLE001
                msg = str(exc)
                if "exception_code=2" in msg:
                    value, status = _("n/a"), _("not available")
                else:
                    value, status = f"{_('error')} {exc}", _("error")
                print(f"  {reg.pnu:5d}  {name:<24} {value}")
                emit(reg, variant, raw="", value=value, status=status, deviation_text=status)
                if status == _("error"):
                    fail += 1
    finally:
        client.close()

    fieldnames = [
        columns["group"],
        columns["name"],
        columns["title"],
        columns["kind"],
        "pnu",
        "addr",
        "raw",
        columns["scale"],
        columns["encoding"],
        columns["value"],
        columns["unit"],
        columns["factory"],
        columns["deviation"],
        columns["range"],
        "a266",
        columns["page"],
        columns["status"],
        columns["description"],
    ]
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(
        "\n"
        + _("Done: {ok} ok, {fail} errors, {changed} changed from factory. Saved to {path}").format(
            ok=ok, fail=fail, changed=changed, path=out_path
        )
    )


if __name__ == "__main__":
    main()
