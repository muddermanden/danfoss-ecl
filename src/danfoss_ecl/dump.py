from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from dotenv import load_dotenv
from pymodbus.client import ModbusSerialClient, ModbusTcpClient
from pymodbus.exceptions import ModbusException

from danfoss_ecl.decode import format_value, in_range, range_text
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
            f"Ingen forbindelse til {settings.host}:{settings.port}"
        )

    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_path = f"ecl310_a266_dump_{stamp}.csv"
    rows: list[dict[str, str | int]] = []
    app = os.getenv("ECL310_APP", "1")

    print(
        f"ECL 310 A266.{app}  {settings.host}:{settings.port}  unit {settings.unit_id}  "
        f"{len(REGISTERS)} PNU'er\n"
    )
    current_group = ""
    ok = 0
    fail = 0

    try:
        for reg in REGISTERS:
            if reg.group != current_group:
                current_group = reg.group
                print(f"\n=== {reg.group} ===")
            if reg.available_on is not None and app not in reg.available_on:
                print(f"  {reg.pnu:5d}  {reg.name:<28} n/a             n/a       {range_text(reg)}")
                rows.append(
                    {
                        "gruppe": reg.group,
                        "navn": reg.name,
                        "pnu": reg.pnu,
                        "addr": reg.pnu - 1,
                        "raw": "",
                        "vaerdi": "n/a",
                        "status": "findes ikke",
                        "omraade": range_text(reg),
                    }
                )
                continue
            try:
                raw = read_holding(client, reg.pnu, settings.unit_id)
                scaled_text = format_value(raw, reg)
                status = in_range(raw, reg)
                print(
                    f"  {reg.pnu:5d}  {reg.name:<28} {scaled_text:<16} "
                    f"{status:<8}  {range_text(reg)}"
                )
                rows.append(
                    {
                        "gruppe": reg.group,
                        "navn": reg.name,
                        "pnu": reg.pnu,
                        "addr": reg.pnu - 1,
                        "raw": raw,
                        "vaerdi": scaled_text,
                        "status": status,
                        "omraade": range_text(reg),
                    }
                )
                ok += 1
            except Exception as exc:  # noqa: BLE001
                msg = str(exc)
                if "exception_code=2" in msg:
                    vaerdi, status = "n/a", "findes ikke"
                else:
                    vaerdi, status = f"FEJL {exc}", "fejl"
                print(f"  {reg.pnu:5d}  {reg.name:<28} {vaerdi}")
                rows.append(
                    {
                        "gruppe": reg.group,
                        "navn": reg.name,
                        "pnu": reg.pnu,
                        "addr": reg.pnu - 1,
                        "raw": "",
                        "vaerdi": vaerdi,
                        "status": status,
                        "omraade": range_text(reg),
                    }
                )
                if status == "fejl":
                    fail += 1
    finally:
        client.close()

    with open(out_path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "gruppe",
                "navn",
                "pnu",
                "addr",
                "raw",
                "vaerdi",
                "status",
                "omraade",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nFærdig: {ok} ok, {fail} fejl. Gemt i {out_path}")


if __name__ == "__main__":
    main()
