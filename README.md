# danfoss-ecl

Register catalog and read-only dump tool for the **Danfoss ECL Comfort 310**, application **A266.x**
(weather-compensated heating + DHW storage tank), over **Modbus TCP** (or RTU).

It documents what the controller exposes: live sensors, outputs, identification and every setting from the
Operating Guide appendix *Parameter ID overview*, with scale, range, OFF encoding and factory value.
`ecl-dump` reads all of it and writes a CSV, so you can see what your controller actually reports and which
settings differ from factory.

It is **not** a Home Assistant integration. For a ready-to-use Home Assistant YAML package built from this
register map, see [muddermanden/homeassistant-danfoss-ecl310](https://github.com/muddermanden/homeassistant-danfoss-ecl310).

Addressing rule from Danfoss: **Modbus register = PNU − 1**.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp ecl310_a266.env.example ecl310_a266.env   # set ECL310_HOST to your controller's IP
ecl-dump
```

Run `ecl-dump` from the folder that holds `ecl310_a266.env`, or point to the file:

```bash
ecl-dump --env-file ~/path/to/ecl310_a266.env
ecl-dump --host 192.168.1.100                # no settings file needed
```

The first line of output says which settings file was used. Without a host, `ecl-dump` stops with an error
instead of guessing.

### With direnv (optional)

The repo ships an [`.envrc`](.envrc) for [direnv](https://direnv.net/). It puts `.venv/bin` on `PATH` and loads
`ecl310_a266.env` whenever you `cd` into the repo, so `ecl-dump` works from any subfolder without activating the venv.

```bash
brew install direnv                                # or your package manager
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc       # bash: direnv hook bash
direnv allow                                       # once, in the repo folder
```

Personal extras go in `.envrc.local` (git-ignored). Run `direnv allow` again after `.envrc` changes.

## Configuration

Settings are `ECL310_*` variables. Highest priority wins:

1. Command line: `--host`
2. Environment variables set in your shell (with direnv, this includes the values from `ecl310_a266.env`)
3. `--env-file FILE`, or otherwise `./ecl310_a266.env` and then `./.env` in the **current folder**
4. Built-in defaults below

`ecl310_a266.env` and `.env` are git-ignored. Only [`ecl310_a266.env.example`](ecl310_a266.env.example) is tracked.

| Variable | Default | Meaning |
|---|---|---|
| `ECL310_MODBUS_MODE` | `tcp` | `tcp` or `rtu` |
| `ECL310_HOST` | **required for tcp** | Controller IP or hostname |
| `ECL310_PORT` | `502` | Modbus TCP port |
| `ECL310_UNIT_ID` | `1` | Unit/slave id. Try `254` (Danfoss service address) if reads fail |
| `ECL310_SERIAL_PORT` | `/dev/tty.usbserial-0001` | RTU only |
| `ECL310_BAUDRATE` / `_PARITY` / `_STOPBITS` / `_BYTESIZE` | `38400` / `N` / `1` / `8` | RTU only |
| `ECL310_APP` | `1` | A266 subtype: `1`, `2`, `9` or `10` |
| `ECL310_LANG` | from `LANG` | `da` or `en` |
| `ECL310_OUTPUT_DIR` | platform data dir | Where CSV dumps go |

## Output

Each run writes `ecl310_a266_dump_<date>_<time>.csv` with these columns: group, name, title, kind, PNU, address,
raw, scale, encoding, value, unit, factory, deviation, range, A266 subtypes, page, status and description.

- Values are scaled and decoded: enums (`ON`/`OFF`/`GEAR`), packed versions, open sensor = 192 °C → `open`
- Settings are compared with the factory value; `-||-` rows in the Danfoss table are subtype variants
- PNUs that do not exist on the selected A266.x are `n/a`

Default output folder (via [platformdirs](https://pypi.org/project/platformdirs/)):

| OS | Path |
|---|---|
| macOS | `~/Library/Application Support/danfoss-ecl/dumps` |
| Linux | `~/.local/share/danfoss-ecl/dumps` |
| Windows | `%APPDATA%\danfoss-ecl\danfoss-ecl\dumps` |

Sample dumps from an A266.1 controller (29 Aug 2026, older column layout, serial number blanked):
[English](examples/a266.1-sample.en.csv), [Danish](examples/a266.1-sample.da.csv).
Tested against a live ECL 310 with software version 2.45 (PNU 35 = 557).

## Languages

Source strings are English (gettext). Translations live in
`src/danfoss_ecl/locale/<lang>/LC_MESSAGES/danfoss_ecl.po`; Danish and English are included.

Set `ECL310_LANG=da` or `en`. If it is unset, `LANG` / `LC_MESSAGES` decides (`da_DK.UTF-8` → `da`).
Unknown codes fall back to English.

To add a language, copy the Danish `.po` file to e.g. `locale/de/LC_MESSAGES/danfoss_ecl.po` and translate
`msgstr`. Then add the code to `SUPPORTED` in `i18n.py`. Regenerate the register strings with
`python3 scripts/write_locales.py` after renaming PNUs.

## Protocol notes

- Function codes: 03 / 04 / 06
- Idle TCP connections are closed by the ECL after ~75 s
- Live sensors: scale 100. Room/DHW setpoints and gains: scale 10. Most other temperatures: scale 1
- Settings in the catalog follow *Parameter ID overview* (not “§7.8”). Factory and range can both change with `-||-` / A266.x
- Identification registers are packed bytes, not a scale factor:

  - PNU 35 software `557` → `2.45` (`major = raw >> 8`, `minor = raw & 0xFF`)
  - PNU 34 hardware same packing (`18692` → `73.04`), **not** the production date
  - PNU 2099 production: high byte = year−2000, low byte = ISO week → Leanheat `32.2025`
  - PNU 2060–2063 application: prefix `'A'`, type `266`, subtype `1`, version packed like software
  - PNU 36+37 serial (high/low)
- `OFF` is `0` when the ON range starts at 1, and `9` when it starts at 10
- Writing is out of scope: a wrong motor running time stalls a valve in its end stop

## Home Assistant

Existing work:

| Project | Covers | Gap |
|---|---|---|
| [HA YAML `modbus`](https://www.home-assistant.io/integrations/modbus/) | Generic registers | You must hand-write every PNU |
| [muddermanden/homeassistant-danfoss-ecl310](https://github.com/muddermanden/homeassistant-danfoss-ecl310) | ECL 310 **A266.x**, YAML package built from this register map | Read-only, plain `modbus:` YAML (not an integration) |
| [acdcnow/Danfoss-ECL-310-for-Home-Assistant](https://github.com/acdcnow/Danfoss-ECL-310-for-Home-Assistant) | ECL 310 **A247.1** | Different application key |
| [JohNan/homeassistant-danfoss_ecl_modbus](https://github.com/JohNan/homeassistant-danfoss_ecl_modbus) | ECL **110** | Different controller |

For a first-class integration, Home Assistant is moving device integrations onto a shared Modbus connection:

- [Developer docs (2026)](https://developers.home-assistant.io/docs/modbus/introduction/)
- [Modernizing Modbus](https://developers.home-assistant.io/blog/2026/07/05/modernizing-modbus/)
- Reference device library: [trovis-modbus](https://github.com/Tom-Bom-badil/trovis-modbus)

## Roadmap

1. **Keep this repo Home Assistant-free:** register map, CLI, and pytest against recorded dumps.
2. **Device library** (`modbus-connection` models: gauges, enums, writable setpoints). No Home Assistant imports.
3. **HACS custom component** that vendors the library, with a config flow for host/port/unit/application key.
4. **Core PR** only after the Home Assistant `modbus_connection` API settles.

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

## License

MIT. Danfoss, ECL Comfort and Leanheat are trademarks of their owners. This project is not affiliated with Danfoss.
