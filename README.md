# danfoss-ecl

Python register map and dump CLI for **Danfoss ECL Comfort 310**, application **A266.1** (weather-compensated heating + DHW storage tank) over **Modbus TCP**.

This is not a Home Assistant integration yet. It is the device knowledge (PNU → Modbus address, scale, range, OFF encoding) needed to build one.

Addressing rule from Danfoss: **Modbus register = PNU − 1**.

## Current status (v0.1)

- Read-only dump of A266.1 holding registers
- Scaled values, enums (`ON`/`OFF`/`GEAR`), open sensor = 192 °C
- PNUs that do not exist on A266.1 are `n/a`
- UI language: Danish and English (gettext `.po` files)
- CSV written to a data directory, not the repo root

Tested against a live ECL 310 at firmware PNU35 = 557.

## Install and dump

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example ecl310_a266.env   # edit host / unit id / language
ecl-dump
```

Unit ID is normally `1`. If the read fails, try `254` (Danfoss service address).

### Language

Source strings are English (gettext). Translations live in:

```
src/danfoss_ecl/locale/<lang>/LC_MESSAGES/danfoss_ecl.po
```

Set in `ecl310_a266.env`:

```
ECL310_LANG=da
```

or `en`. If unset, `LANG` / `LC_MESSAGES` is used (`da_DK.UTF-8` → `da`). Unknown codes fall back to English.

To add a language, copy the Danish `.po` file to e.g. `locale/de/LC_MESSAGES/danfoss_ecl.po` and translate `msgstr`. Then add the code to `SUPPORTED` in `i18n.py`. Regenerate register strings with `python3 scripts/write_locales.py` after renaming PNUs.

### CSV output directory

Default (via [platformdirs](https://pypi.org/project/platformdirs/)):

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/danfoss-ecl/dumps` |
| Linux | `~/.local/share/danfoss-ecl/dumps` |
| Windows | `%APPDATA%\danfoss-ecl\danfoss-ecl\dumps` |

Override:

```
ECL310_OUTPUT_DIR=~/varme/dumps
```

A checked-in snapshot (Danish headers, A266.1, 29 Aug 2026) is in [examples/a266.1-sample.da.csv](examples/a266.1-sample.da.csv).

## What already exists in Home Assistant

A proper A266.1 integration is still missing. Nearby work:

| Project | Covers | Gap |
|---|---|---|
| [HA YAML `modbus`](https://www.home-assistant.io/integrations/modbus/) | Generic registers | You must hand-write every PNU |
| [acdcnow/Danfoss-ECL-310-for-Home-Assistant](https://github.com/acdcnow/Danfoss-ECL-310-for-Home-Assistant) | ECL 310 **A247.1** | Different application key |
| [JohNan/homeassistant-danfoss_ecl_modbus](https://github.com/JohNan/homeassistant-danfoss_ecl_modbus) | ECL **110** | Different controller |

Do not start from YAML `modbus:` if the goal is a first-class integration. HA is moving device integrations onto a shared Modbus connection:

- [Developer docs (2026)](https://developers.home-assistant.io/docs/modbus/introduction/)
- [Modernizing Modbus](https://developers.home-assistant.io/blog/2026/07/05/modernizing-modbus/)
- Reference device library: [trovis-modbus](https://github.com/Tom-Bom-badil/trovis-modbus)

## Winter roadmap

1. **Keep this repo HA-free.** Register map + CLI + pytest against recorded dumps.
2. **Device library** (`modbus-connection` models: gauges, enums, writeable setpoints). No Home Assistant imports.
3. **HACS custom component** that vendors the library, config flow for host/port/unit/application key.
4. **Core PR** only after the HA `modbus_connection` API settles (their own blog currently says to wait on wiring).

Useful first entities for A266.1:

| Entity | PNU | Notes |
|---|---|---|
| Outdoor / flow / tank | 10201, 10203, 10204 | scale 100 |
| Desired flow | 11253 | scale 100 |
| Room / DHW setpoints | 11180, 12190 | scale 10, writable later |
| Heat curve, min/max flow | 11175, 11177, 11178 | |
| Motor running time / NZ | 11186, 11187, 12186, 12187 | the humming-valve pair |
| Pumps | relays 4006, 4007 | |
| Valve estimate | not ECA32 AO | 3-point gear motors; Leanheat % is estimated |

Do not treat ECA32 AO1–AO3 as V1/V2 unless analog actuators are actually wired.

## Protocol notes

- Function codes: 03 / 04 / 06
- Idle TCP connections are closed by the ECL after ~75 s
- Live sensors: scale 100. Room/DHW setpoints and gains: scale 10. Most other temperatures: scale 1
- Identification registers are packed bytes, not a scale factor:
  - PNU 35 software `557` → `2.45` (`major = raw >> 8`, `minor = raw & 0xFF`)
  - PNU 34 hardware same packing (`18692` → `73.04`), **not** the production date
  - PNU 2099 production: high byte = year−2000, low byte = ISO week → Leanheat `32.2025`
  - PNU 2060–2063 application: prefix `'A'`, type `266`, subtype `1`, version packed like software
  - PNU 36+37 serial (high/low)
- `OFF` is `0` when the ON range starts at 1, and `9` when it starts at 10
- Write support is out of scope for v0.1 (wrong motor runtime will stall a valve in end stop)

## License

MIT. Danfoss, ECL Comfort and Leanheat are trademarks of their owners. This project is not affiliated with Danfoss.
