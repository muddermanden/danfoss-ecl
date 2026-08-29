from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pymodbus.client import ModbusSerialClient, ModbusTcpClient
from pymodbus.exceptions import ModbusException

from danfoss_ecl.decode import format_value, in_range, range_text
from danfoss_ecl.i18n import _, setup_i18n
from danfoss_ecl.paths import dump_dir
from danfoss_ecl.registers_a266 import REGISTERS


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


def load_settings() -> ModbusSettings:
    load_dotenv("ecl310_a266.env")
    load_dotenv(".env")
    load_dotenv()
    mode = os.getenv("ECL310_MODBUS_MODE", "tcp").lower()
    if mode not in {"tcp", "rtu"}:
        raise ValueError("ECL310_MODBUS_MODE must be either 'tcp' or 'rtu'")

    lang = setup_i18n()
    return ModbusSettings(
        mode=mode,  # type: ignore[arg-type]
        unit_id=env_int("ECL310_UNIT_ID", 1),
        host=os.getenv("ECL310_HOST", "192.168.1.100"),
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


def main() -> None:
    settings = load_settings()
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

    col_group = _("group")
    col_name = _("name")
    col_value = _("value")
    col_status = _("status")
    col_range = _("range")

    print(
        f"ECL 310 A266.{app}  {settings.host}:{settings.port}  "
        f"{_('unit')} {settings.unit_id}  "
        f"{_('{count} PNUs').format(count=len(REGISTERS))}  [{settings.lang}]\n"
    )
    current_group = ""
    ok = 0
    fail = 0

    try:
        for reg in REGISTERS:
            group = _(reg.group)
            name = _(reg.name)
            if reg.group != current_group:
                current_group = reg.group
                print(f"\n=== {group} ===")
            if reg.available_on is not None and app not in reg.available_on:
                status = _("not available")
                value = _("n/a")
                print(f"  {reg.pnu:5d}  {name:<28} {value:<16} {status:<12}  {range_text(reg)}")
                rows.append(
                    {
                        col_group: group,
                        col_name: name,
                        "pnu": reg.pnu,
                        "addr": reg.pnu - 1,
                        "raw": "",
                        col_value: value,
                        col_status: status,
                        col_range: range_text(reg),
                    }
                )
                continue
            try:
                raw = read_holding(client, reg.pnu, settings.unit_id)
                scaled_text = format_value(raw, reg)
                status = in_range(raw, reg)
                print(
                    f"  {reg.pnu:5d}  {name:<28} {scaled_text:<16} "
                    f"{status:<12}  {range_text(reg)}"
                )
                rows.append(
                    {
                        col_group: group,
                        col_name: name,
                        "pnu": reg.pnu,
                        "addr": reg.pnu - 1,
                        "raw": raw,
                        col_value: scaled_text,
                        col_status: status,
                        col_range: range_text(reg),
                    }
                )
                ok += 1
            except Exception as exc:  # noqa: BLE001
                msg = str(exc)
                if "exception_code=2" in msg:
                    value, status = _("n/a"), _("not available")
                else:
                    value, status = f"{_('error')} {exc}", _("error")
                print(f"  {reg.pnu:5d}  {name:<28} {value}")
                rows.append(
                    {
                        col_group: group,
                        col_name: name,
                        "pnu": reg.pnu,
                        "addr": reg.pnu - 1,
                        "raw": "",
                        col_value: value,
                        col_status: status,
                        col_range: range_text(reg),
                    }
                )
                if status == _("error"):
                    fail += 1
    finally:
        client.close()

    fieldnames = [
        col_group,
        col_name,
        "pnu",
        "addr",
        "raw",
        col_value,
        col_status,
        col_range,
    ]
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(
        "\n"
        + _("Done: {ok} ok, {fail} errors. Saved to {path}").format(
            ok=ok, fail=fail, path=out_path
        )
    )


if __name__ == "__main__":
    main()
