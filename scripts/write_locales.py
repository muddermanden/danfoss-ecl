#!/usr/bin/env python3
"""Generate gettext .po files from the English register map + extra UI strings."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from danfoss_ecl.registers_a266 import REGISTERS  # noqa: E402

HEADER = """# {lang_name} translations for danfoss-ecl.
# Copyright (C) 2026 danfoss-ecl contributors
# This file is distributed under the same license as the danfoss-ecl package.
msgid ""
msgstr ""
"Project-Id-Version: danfoss-ecl 0.1.0\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: {date}\\n"
"PO-Revision-Date: {date}\\n"
"Last-Translator: \\n"
"Language-Team: {lang}\\n"
"Language: {lang}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

"""

# English msgid -> Danish
DA = {
    "Sensors": "Føler",
    "Outputs": "Udgang",
    "Operation": "Drift",
    "System": "System",
    "Floor drying": "Gulvtørring",
    "Heating": "Varme",
    "DHW": "VV",
    "S1 outdoor raw": "S1 ude rå",
    "S2 room raw": "S2 rum rå",
    "S3 heating flow raw": "S3 frem varme rå",
    "S4 DHW / tank raw": "S4 frem/beholder VV rå",
    "S5 heating return raw": "S5 retur varme rå",
    "S6 DHW return raw": "S6 retur VV rå",
    "S7 raw": "S7 rå",
    "S8 raw": "S8 rå",
    "S9 raw": "S9 rå",
    "S10 raw": "S10 rå",
    "S1 circuit view": "S1 kredsvisning",
    "S2 circuit view": "S2 kredsvisning",
    "S3 circuit view": "S3 kredsvisning",
    "S4 circuit view": "S4 kredsvisning",
    "S5 circuit view": "S5 kredsvisning",
    "S6 circuit view": "S6 kredsvisning",
    "S3 desired flow": "S3 ønsket frem",
    "S4 desired flow": "S4 ønsket frem",
    "ECA32 AO1 status %": "ECA32 AO1 status %",
    "ECA32 AO2 status %": "ECA32 AO2 status %",
    "ECA32 AO3 status %": "ECA32 AO3 status %",
    "Triac 1": "Triac 1",
    "Triac 2": "Triac 2",
    "Triac 3": "Triac 3",
    "Triac 4": "Triac 4",
    "Relay 1": "Relæ 1",
    "Relay 2": "Relæ 2",
    "Relay 3": "Relæ 3",
    "Relay 4": "Relæ 4",
    "Digital output bitmask 3998": "Digital udgang bitmaske 3998",
    "Digital output bitmask 3999": "Digital udgang bitmaske 3999",
    "Mode circuit 1": "Mode kreds 1",
    "Mode circuit 2": "Mode kreds 2",
    "Status circuit 1": "Status kreds 1",
    "Status circuit 2": "Status kreds 2",
    "Modbus address": "Modbus-adresse",
    "Software version": "Softwareversion",
    "Hardware revision": "Hardware-revision",
    "Program running": "Programafvikling",
    "Max. power failure": "Maks. pwr. fejl",
    "Ramp X5-X6": "Rampe X5-X6",
    "Ramp X7-X8": "Rampe X7-X8",
    "Application continued": "Appl. fortsat",
    "After power failure": "Efter strømsvigt",
    "Desired T": "Ønsket T",
    "ECA address": "ECA-adresse",
    "Auto saving": "Auto-spare",
    "Boost": "Boost",
    "Ramp": "Rampe",
    "Optimizer": "Optimizer",
    "Integrator time 11015": "Intgr. tid 11015",
    "Slave difference": "Slave differens",
    "Based on": "Baseret på",
    "Total stop": "Totalstop",
    "Pump exercise": "Pumpe-motion",
    "Valve exercise": "Ventil-motion",
    "Actuator type": "Motortype",
    "Pre-stop": "Pre-stop",
    "Const. T return limit": "Kon. T retur T gr.",
    "DHW return limit": "VV retur T grænse",
    "High outdoor T X1": "Høj ude T X1",
    "Low limit Y1": "Nedre grænse Y1",
    "Low outdoor T X2": "Lav ude T X2",
    "High limit Y2": "Øvre grænse Y2",
    "Max. influence 11035": "Maks. forstærkn. 11035",
    "Min. influence 11036": "Min. forstærkn. 11036",
    "Integrator time 11037": "Intgr. tid 11037",
    "Pump postrun": "Pumpe efterløb",
    "Parallel operation": "Parallel drift",
    "Pump demand": "Pumpe krav",
    "DHW priority": "VV-prioritet",
    "Pump frost T": "Pumpe frost T",
    "Pump start T": "Pumpe start T",
    "Max. flow T": "Maks. frem T",
    "Delay 11080": "Forsinkelse 11080",
    "Priority 11085": "Prioritet 11085",
    "Frost protection T": "Frostbeskyt. T",
    "Input type": "Input type",
    "Integrator time 11112": "Intgr. tid 11112",
    "Filter constant": "Filter konstant",
    "Pulse": "Puls",
    "Units": "Enheder",
    "High limit Y2 flow": "Øvre grænse Y2 flow",
    "Low limit Y1 flow": "Nedre grænse Y1 flow",
    "Low outdoor T X2 flow": "Lav ude T X2 flow",
    "High outdoor T X1 flow": "Høj ude T X1 flow",
    "External override": "Ekst. overstyring",
    "External mode": "Ekst. drift",
    "Upper difference": "Øvre differens",
    "Lower difference": "Nedre differens",
    "Delay 11149": "Forsinkelse 11149",
    "Cancel T": "Annullerings T",
    "Motor protection": "Motorbeskyttelse",
    "Heat curve slope": "Varmekurve hældning",
    "Min. temperature": "Min. temperatur",
    "Max. temperature": "Maks. temperatur",
    "Heat cut-out": "Varme-udkobling",
    "Desired room comfort": "Ønsket rum komfort",
    "Desired room saving": "Ønsket rum spare",
    "Max. influence 11182": "Maks. forstærkn. 11182",
    "Min. influence 11183": "Min. forstærkn. 11183",
    "Motor running time": "Motor-køretid",
    "Neutral zone": "Neutralzone",
    "Min. running time": "Min. køretid",
    "Summer start mm": "Sommer start mm",
    "Summer start dd": "Sommer start dd",
    "Summer filter": "Sommer filter",
    "Winter start mm": "Vinter start mm",
    "Winter start dd": "Vinter start dd",
    "Winter cut-out T": "Vinter udk. T",
    "Winter filter": "Vinter filter",
    "Send desired T": "Send ønsket T",
    "Screed circuit": "Kreds Estrich",
    "Return limit": "Grænse retur",
    "Max. influence": "Maks. forstærkn.",
    "Min. influence": "Min. forstærkn.",
    "Integrator time 12037": "Intgr. tid 12037",
    "Priority": "Prioritet",
    "Opening time": "Åbne-tid",
    "Closing time": "Lukke-tid",
    "Tn idle": "Tn tomgang",
    "Supply T idle": "Forsyn. T tomgang",
    "Limit 12111": "Grænse 12111",
    "Integrator time 12112": "Intgr. tid 12112",
    "Anti-bacteria day": "Anti-bakt. dag",
    "Anti-bacteria start": "Anti-bakt. start",
    "Anti-bacteria duration": "Anti-bakt. varighed",
    "Anti-bacteria desired T": "Anti-bakt. ønsket T",
    "Delay": "Forsinkelse",
    "Autotuning": "Autotuning",
    "Desired DHW comfort": "Ønsket VV komfort",
    "Desired DHW saving": "Ønsket VV spare",
    "open": "åben",
    "ok": "ok",
    "out of range": "udenfor",
    "n/a": "n/a",
    "not available": "findes ikke",
    "error": "fejl",
    "OFF": "OFF",
    "ON": "ON",
    "group": "gruppe",
    "name": "navn",
    "value": "værdi",
    "status": "status",
    "range": "område",
    "Could not connect to {host}:{port}": "Ingen forbindelse til {host}:{port}",
    "Done: {ok} ok, {fail} errors. Saved to {path}": "Færdig: {ok} ok, {fail} fejl. Gemt i {path}",
    "{count} PNUs": "{count} PNU'er",
    "unit": "unit",
}


def po_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def write_po(path: Path, lang: str, lang_name: str, catalog: dict[str, str]) -> None:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M+0000")
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    extra = [
        "open",
        "ok",
        "out of range",
        "n/a",
        "not available",
        "error",
        "OFF",
        "ON",
        "group",
        "name",
        "value",
        "status",
        "range",
        "Could not connect to {host}:{port}",
        "Done: {ok} ok, {fail} errors. Saved to {path}",
        "{count} PNUs",
        "unit",
        "X1",
        "X2",
        "X3",
        "X4",
        "X5",
        "X6",
        "X7",
        "X8",
        "Xp",
        "Tn",
        "Boost",
        "Ramp",
        "Optimizer",
        "Pre-stop",
        "Input type",
        "Filter constant",
        "Pulse",
        "Units",
        "Autotuning",
    ]
    for msgid in extra:
        if msgid not in seen:
            entries.append((msgid, catalog.get(msgid, msgid)))
            seen.add(msgid)
    for reg in REGISTERS:
        for msgid in (reg.group, reg.name):
            if msgid not in seen:
                entries.append((msgid, catalog.get(msgid, msgid)))
                seen.add(msgid)
    path.parent.mkdir(parents=True, exist_ok=True)
    chunks = [HEADER.format(lang=lang, lang_name=lang_name, date=date)]
    for msgid, msgstr in entries:
        chunks.append(f'msgid "{po_escape(msgid)}"\nmsgstr "{po_escape(msgstr)}"\n\n')
    path.write_text("".join(chunks), encoding="utf-8")


def main() -> None:
    locale = ROOT / "src" / "danfoss_ecl" / "locale"
    write_po(locale / "da" / "LC_MESSAGES" / "danfoss_ecl.po", "da", "Danish", DA)
    write_po(locale / "en" / "LC_MESSAGES" / "danfoss_ecl.po", "en", "English", {})
    print("wrote locale files")


if __name__ == "__main__":
    main()
