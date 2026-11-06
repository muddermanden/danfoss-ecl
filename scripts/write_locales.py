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

# English msgid -> Danish. Appendix Parameter Name kept short like the ECL display.
DA = {
    "Sensors": "Føler",
    "Outputs": "Udgang",
    "Operation": "Drift",
    "System": "System",
    "Floor drying": "Gulvtørring",
    "Heating": "Varme",
    "DHW": "VV",
    "setting": "indstilling",
    "live": "live",
    "output": "udgang",
    "ident": "identitet",
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
    "Relay 1: P1 circulation pump, DHW, circuit 2": "Relæ 1: P1 cirkulationspumpe, brugsvand, kreds 2",
    "Relay 2: P2 circulation pump, heating, circuit 1": "Relæ 2: P2 cirkulationspumpe, varme, kreds 1",
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
    "Software build": "Software-build",
    "Serial high": "Serienummer høj",
    "Serial low": "Serienummer lav",
    "Production week/year": "Produktionsdato",
    "Application prefix": "Applikationspræfiks",
    "Application type": "Applikationstype",
    "Application subtype": "Applikationsundertype",
    "Application version": "Applikationsversion",
    "Prog. execution": "Prog. afvikling",
    "Max. pwr. failure": "Maks. pwr. fejl",
    "Ramp X5-X6": "Rampe X5-X6",
    "Ramp X7-X8": "Rampe X7-X8",
    "Appl. continue": "Appl. fortsat",
    "After power fail.": "Efter strømsvigt",
    "Desired T": "Ønsket T",
    "ECA addr.": "ECA-adr.",
    "Auto saving": "Auto-spare",
    "Boost": "Boost",
    "Ramp": "Rampe",
    "Optimizer": "Optimizer",
    "Adapt. time": "Adapt. tid",
    "Adapt. time (return)": "Adapt. tid (retur)",
    "Adapt. time (flow)": "Adapt. tid (flow)",
    "Demand offset": "Demand offset",
    "Based on": "Baseret på",
    "Total stop": "Totalstop",
    "P exercise": "P-motion",
    "M exercise": "M-motion",
    "Actuator": "Aktuator",
    "Pre-stop": "Pre-stop",
    "Con. T, ret. T lim.": "Kon. T, ret. T gr.",
    "DHW, ret. T limit": "VV retur T grænse",
    "High T out X1": "Høj ude T X1",
    "Low limit Y1": "Nedre grænse Y1",
    "Low T out X2": "Lav ude T X2",
    "High limit Y2": "Øvre grænse Y2",
    "Infl. - max.": "Forst. - maks.",
    "Infl. - min.": "Forst. - min.",
    "Infl. - max. (room)": "Forst. - maks. (rum)",
    "Infl. - min. (room)": "Forst. - min. (rum)",
    "P post-run": "P-efterløb",
    "Parallel operation": "Parallel drift",
    "P demand": "P-krav",
    "DHW priority": "VV-prioritet",
    "P frost T": "P-frost T",
    "P heat T": "P-varme T",
    "Max. flow T": "Maks. frem T",
    "Delay": "Forsinkelse",
    "Delay (alarm)": "Forsinkelse (alarm)",
    "Priority": "Prioritet",
    "Frost pr. T": "Frostbesk. T",
    "Input type": "Input type",
    "Filter constant": "Filter konstant",
    "Pulse": "Puls",
    "Units": "Enheder",
    "High limit Y2 (flow)": "Øvre grænse Y2 (flow)",
    "Low limit Y1 (flow)": "Nedre grænse Y1 (flow)",
    "Low T out X2 (flow)": "Lav ude T X2 (flow)",
    "High T out X1 (flow)": "Høj ude T X1 (flow)",
    "Ext. input": "Ext. indgang",
    "Ext. mode": "Ext. tilstand",
    "Upper difference": "Øvre differens",
    "Lower difference": "Nedre differens",
    "Lowest temp.": "Laveste temp.",
    "Motor pr.": "Motorbesk.",
    "Heat curve": "Varmekurve",
    "Temp. min.": "Temp. min.",
    "Temp. max.": "Temp. maks.",
    "Summer, cut-out": "Sommer, udkobling",
    "Desired room comfort": "Ønsket rum komfort",
    "Desired room saving": "Ønsket rum spare",
    "Xp": "Xp",
    "Tn": "Tn",
    "M run": "M-gang",
    "Nz": "Nz",
    "Min. act. time": "Min. akt. tid",
    "Sum. start, month": "Som. start, måned",
    "Sum. start, day": "Som. start, dag",
    "Summer, filter": "Sommer, filter",
    "Win. start, month": "Vin. start, måned",
    "Winter start, day": "Vinter start, dag",
    "Winter, cut-out": "Vinter, udkobling",
    "Winter, filter": "Vinter, filter",
    "Send desired T": "Send ønsket T",
    "Pressure": "Tryk",
    "Low X": "Low X",
    "High X": "High X",
    "Low Y": "Low Y",
    "High Y": "High Y",
    "Alarm high": "Alarm høj",
    "Alarm low": "Alarm lav",
    "Alarm time-out": "Alarm time-out",
    "Alarm time-out (digital)": "Alarm time-out (digital)",
    "Digital": "Digital",
    "Alarm value": "Alarmværdi",
    "Circuit, Estrich.": "Kreds, Estrich.",
    "Limit": "Grænse",
    "Limit (flow)": "Grænse (flow)",
    "Open time": "Åbne-tid",
    "Close time": "Lukke-tid",
    "Tn (idle)": "Tn (tomgang)",
    "Supply T (idle)": "Forsyn. T (tomgang)",
    "Day": "Dag",
    "Start time": "Starttid",
    "Duration": "Varighed",
    "Auto tuning": "Autotuning",
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
    "factory": "fabrik",
    "changed": "ændret",
    "group": "gruppe",
    "name": "navn",
    "title": "titel",
    "kind": "type",
    "value": "værdi",
    "unit": "enhed",
    "scale": "skala",
    "encoding": "encoding",
    "deviation": "afvigelse",
    "range": "område",
    "page": "side",
    "status": "status",
    "description": "beskrivelse",
    "Could not connect to {host}:{port}": "Ingen forbindelse til {host}:{port}",
    "Done: {ok} ok, {fail} errors, {changed} changed from factory. Saved to {path}": (
        "Færdig: {ok} ok, {fail} fejl, {changed} afviger fra fabrik. Gemt i {path}"
    ),
    "{count} PNUs": "{count} PNU'er",
    "Settings: {files}": "Indstillinger: {files}",
    "Settings: no settings file found, using environment variables only": (
        "Indstillinger: ingen indstillingsfil fundet, bruger kun miljøvariabler"
    ),
    "Parameter ID overview": "Parameter-ID, oversigt",
}


EXTRA = [
    "open",
    "ok",
    "out of range",
    "n/a",
    "not available",
    "error",
    "OFF",
    "ON",
    "factory",
    "changed",
    "group",
    "name",
    "title",
    "kind",
    "value",
    "unit",
    "scale",
    "encoding",
    "deviation",
    "range",
    "page",
    "status",
    "description",
    "setting",
    "live",
    "output",
    "ident",
    "Could not connect to {host}:{port}",
    "Done: {ok} ok, {fail} errors, {changed} changed from factory. Saved to {path}",
    "{count} PNUs",
    "Parameter ID overview",
    "Settings: {files}",
    "Settings: no settings file found, using environment variables only",
]


def po_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def collect_msgids() -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []

    def add(msgid: str) -> None:
        if msgid and msgid not in seen:
            seen.add(msgid)
            ordered.append(msgid)

    for msgid in EXTRA:
        add(msgid)
    for reg in REGISTERS:
        add(reg.group)
        add(reg.name)
        add(reg.title)
        add(reg.description)
        add(reg.kind)
        for variant in reg.variants:
            if variant.choices:
                for choice in variant.choices:
                    add(choice)
    return ordered


def write_po(path: Path, lang: str, lang_name: str, catalog: dict[str, str]) -> None:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M+0000")
    chunks = [HEADER.format(lang=lang, lang_name=lang_name, date=date)]
    for msgid in collect_msgids():
        msgstr = catalog.get(msgid, msgid)
        chunks.append(f'msgid "{po_escape(msgid)}"\nmsgstr "{po_escape(msgstr)}"\n\n')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(chunks), encoding="utf-8")


def main() -> None:
    locale = ROOT / "src" / "danfoss_ecl" / "locale"
    write_po(locale / "da" / "LC_MESSAGES" / "danfoss_ecl.po", "da", "Danish", DA)
    write_po(locale / "en" / "LC_MESSAGES" / "danfoss_ecl.po", "en", "English", {})
    print("wrote locale files")


if __name__ == "__main__":
    main()
