# danfoss-ecl

**See everything your Danfoss ECL Comfort 310 knows, and which settings differ from factory, with one read-only
command.**

```text
$ ecl-dump
Settings: /home/you/danfoss-ecl/ecl310_a266.env
ECL 310 A266.1  192.168.1.100:502  unit 1  186 PNUs  [en]

=== Sensors ===
  10201  S1 outdoor raw           7.30 °C          ok            -60 … 150 °C
  10202  S2 room raw              open             open          -60 … 150 °C
  10203  S3 heating flow raw      40.48 °C         ok            -60 … 150 °C
  10204  S4 DHW / tank raw        58.38 °C         ok            -60 … 150 °C
…
=== Heating ===
 *11177  Temp. min.               28 °C            changed       10 … 150 °C  factory 10 °C
 *11178  Temp. max.               70 °C            changed       10 … 150 °C  factory 90 °C
…
Done: 164 ok, 0 errors, 11 changed from factory. Saved to …/dumps/ecl310_a266_dump_2026-11-06_161718.csv
```

`danfoss-ecl` is a register catalog and a dump tool for the **ECL Comfort 310** district-heating controller running
application **A266.x**. It reads every live value and setting over **Modbus**, scales and decodes them, compares
each setting with its factory value, and saves it all as a CSV. `*` marks a setting that differs from factory.

It only **reads**: it never writes to the controller. Tested on one ECL Comfort 310 with A266.1 (software 2.45).

## Quick start

You need Python 3.11 or newer, and the controller on your network (see [Requirements](#requirements)).

```bash
git clone https://github.com/muddermanden/danfoss-ecl.git
cd danfoss-ecl
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/ecl-dump --host 192.168.1.100      # your controller's IP address
```

The table above is printed to the terminal, and the CSV path is on the last line.

To skip `--host` next time, save your settings in a file:

```bash
cp ecl310_a266.env.example ecl310_a266.env   # then set ECL310_HOST in it
.venv/bin/ecl-dump
```

`ecl310_a266.env` is git-ignored, so your IP address stays private. `ecl-dump` reads it from the folder you run it
in, and the first line of output tells you which file it used.

### With direnv (optional)

The repo includes an [`.envrc`](.envrc) for [direnv](https://direnv.net/). With it, entering the repo folder puts
`.venv/bin` on your `PATH` and loads `ecl310_a266.env`, so plain `ecl-dump` works in any subfolder.

```bash
brew install direnv                              # or your package manager
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc     # bash: eval "$(direnv hook bash)" in ~/.bashrc
direnv allow                                     # once, in the repo folder
```

Put personal additions in `.envrc.local` (git-ignored). Run `direnv allow` again after `.envrc` changes.

## Requirements

| What | Details |
|---|---|
| Controller | Danfoss **ECL Comfort 310** running application **A266.x**. Other applications have other registers |
| Connection | Modbus TCP over the controller's Ethernet (TCP port **502**), or Modbus RTU over RS-485 |
| Address | A known IP address for the controller; a DHCP reservation in your router keeps it fixed |
| Python | 3.11 or newer |

### Words you'll meet

| Term | Meaning |
|---|---|
| **A266.x** | The ECL *application*: the program the controller runs. A266 is space heating plus domestic hot water (DHW); `.1`, `.2`, `.9` and `.10` are variants of it |
| **PNU** | Danfoss *parameter number*, as listed in the ECL documentation. The Modbus register is **PNU − 1** |
| **Factory value** | The setting as delivered, from the Operating Guide appendix *Parameter ID overview* |
| **`-||-` row** | In that Danfoss table, a row that repeats the parameter above with another factory value or range for another A266 variant. The catalog stores these as *variants* |
| **S1–S10** | Temperature sensor inputs. In A266.1: S1 outdoor, S2 room, S3 heating flow, S4 DHW flow, S5/S6 return |
| **M1/M2, P1/P2, A1** | Valve motors, circulation pumps and alarm relay |
| **Unit id** | The Modbus address of the controller: normally `1`, or `254` (the Danfoss service address) |

## Configuration

Settings are `ECL310_*` variables, set in `ecl310_a266.env` (see
[`ecl310_a266.env.example`](ecl310_a266.env.example)) or in your shell.

| Variable | Default | Meaning |
|---|---|---|
| `ECL310_HOST` | **required** for TCP | Controller IP address or hostname |
| `ECL310_PORT` | `502` | Modbus TCP port |
| `ECL310_UNIT_ID` | `1` | Modbus unit id; try `254` if reads fail |
| `ECL310_APP` | `1` | A266 variant: `1`, `2`, `9` or `10` |
| `ECL310_LANG` | from `LANG` | Output language, `en` or `da` |
| `ECL310_OUTPUT_DIR` | see [Output](#output) | Folder for the CSV files |
| `ECL310_MODBUS_MODE` | `tcp` | `tcp`, or `rtu` for RS-485 |
| `ECL310_SERIAL_PORT`, `_BAUDRATE`, `_PARITY`, `_STOPBITS`, `_BYTESIZE` | `/dev/tty.usbserial-0001`, `38400`, `N`, `1`, `8` | RTU only |

When the same setting comes from several places, the first one wins:

1. `--host` on the command line
2. Variables already set in your shell (with direnv, that includes `ecl310_a266.env`)
3. `--env-file FILE`, or else `./ecl310_a266.env` and then `./.env` in the current folder
4. The defaults above

## Output

Each run saves `ecl310_a266_dump_<date>_<time>.csv` in:

| OS | Folder |
|---|---|
| macOS | `~/Library/Application Support/danfoss-ecl/dumps` |
| Linux | `~/.local/share/danfoss-ecl/dumps` |
| Windows | `%APPDATA%\danfoss-ecl\danfoss-ecl\dumps` |

A few rows:

```csv
group,name,title,kind,pnu,addr,raw,scale,encoding,value,unit,factory,deviation,range,a266,page,status,description
Sensors,S1 outdoor raw,Outdoor temperature,live,10201,10200,730,100,scaled,7.30 °C,°C,,,-60 … 150 °C,"1, 2, 9, 10",,ok,"Pt 1000 outdoor sensor, raw."
Heating,Temp. min.,Minimum flow temperature,setting,11177,11176,28,1,scaled,28 °C,°C,10 °C,changed,10 … 150 °C,"1, 2, 9, 10",74,ok,Desired flow will not go below this. Has higher priority than the heat curve.
```

| Column | Meaning |
|---|---|
| `group`, `name`, `title` | Where the register belongs, its short name as on the ECL display, and a longer title |
| `kind` | `live` (measured), `output` (relay, valve), `setting` or `ident` (identification) |
| `pnu`, `addr` | Danfoss parameter number and Modbus register (PNU − 1) |
| `raw`, `scale`, `encoding` | The register value as read, and how it is turned into `value` |
| `value`, `unit` | The decoded value, for example `7.30 °C`, `ON` or `2.45` |
| `factory`, `deviation` | The factory value, and `changed` when the setting differs from it |
| `range`, `a266` | Allowed range, and the A266 variants that have this register |
| `page`, `status`, `description` | Page in the Operating Guide; `ok`, `open`, `out of range`, `n/a` or `error`; and what the register does |

`open` means an unconnected sensor (the ECL reads 192 °C). `n/a` means the register doesn't exist in your A266
variant.

Sample dumps from an A266.1 controller, in an older column layout and with the serial number blanked:
[English](examples/a266.1-sample.en.csv), [Danish](examples/a266.1-sample.da.csv).

## Troubleshooting

**`ecl-dump: No controller address`**
Pass `--host`, or set `ECL310_HOST` in `ecl310_a266.env` in the folder you run from.

**`Could not connect to 192.168.1.100:502`**
The controller doesn't answer on that address. Check the IP, that it answers a ping, and that nothing blocks TCP
port 502 between your computer and the controller (a firewall or a separate VLAN, for example).

**It connects, but every register shows `error`.**
Try the Danfoss service address: `ECL310_UNIT_ID=254 ecl-dump`.

**Many registers show `n/a`.**
`ECL310_APP` doesn't match your controller. The *Application* rows in the System group show the real one, for
example `A`, `266`, `1` for A266.1.

**The connection drops when idle.**
The ECL closes idle TCP connections after about 75 seconds. `ecl-dump` reads everything in one go, so this only
matters if you build on the library.

## Languages

Output is in English or Danish: `ECL310_LANG=en` or `da`. If it isn't set, your system's `LANG` decides
(`da_DK.UTF-8` gives Danish), and anything else falls back to English.

To add a language:

1. Copy `src/danfoss_ecl/locale/da/LC_MESSAGES/danfoss_ecl.po` to `locale/<code>/LC_MESSAGES/` and translate each
   `msgstr`.
2. Add the code to `SUPPORTED` in `src/danfoss_ecl/i18n.py`.

After renaming registers, regenerate the strings with `python3 scripts/write_locales.py`.

## Development

```bash
.venv/bin/pip install -e ".[dev]"
.venv/bin/python -m pytest
```

The tests run without a controller.

## Protocol notes

- Modbus register = PNU − 1. `ecl-dump` reads holding registers only (function code 03).
- Live sensors use scale 100, room and DHW setpoints and gains scale 10, most other temperatures scale 1.
- The catalog follows the Operating Guide appendix *Parameter ID overview*. Factory value and range can differ
  between A266 variants (`-||-` rows).
- Identification registers are packed bytes, not scaled values:
  - PNU 35 software: `557` → `2.45` (`major = raw >> 8`, `minor = raw & 0xFF`)
  - PNU 34 hardware: the same packing (`18692` → `73.04`); it is **not** the production date
  - PNU 2099 production date: high byte = year − 2000, low byte = ISO week → `32.2025`
  - PNU 2060–2063 application: prefix `'A'`, type `266`, variant `1`, version packed like the software
  - PNU 36 and 37: serial number, high and low word
- `OFF` is `0` when the ON range starts at 1, and `9` when it starts at 10.
- M1/M2 are 3-point valve motors: the valve position Leanheat shows is an estimate. Don't read ECA32 analog
  outputs AO1–AO3 as V1/V2 unless analog actuators are actually wired to them.
- Writing is deliberately out of scope: for example, a wrong motor running time drives a valve into its end stop.

## Home Assistant

This tool doesn't need Home Assistant. To get the ECL into Home Assistant, use the companion repository:

| Repository | What it is | Use it when |
|---|---|---|
| **danfoss-ecl** (this one) | Python register catalog and `ecl-dump` command | You want to check a controller, document its settings or look up a register |
| [homeassistant-danfoss-ecl310](https://github.com/muddermanden/homeassistant-danfoss-ecl310) | Home Assistant YAML package and dashboards | You want the ECL in Home Assistant |

The package's register addresses, scales and decoding come from this catalog. The two are **independent**: they
share no code, and neither needs the other to run. `ecl-dump` is a quick way to check that a controller answers
before you set up the package.

Other projects for Danfoss ECL in Home Assistant cover other hardware:
[acdcnow/Danfoss-ECL-310-for-Home-Assistant](https://github.com/acdcnow/Danfoss-ECL-310-for-Home-Assistant)
(ECL 310, application A247.1) and
[JohNan/homeassistant-danfoss_ecl_modbus](https://github.com/JohNan/homeassistant-danfoss_ecl_modbus) (ECL 110).

## Roadmap

1. Keep this repository free of Home Assistant code: register catalog, CLI, and tests against recorded dumps.
2. A device library on Home Assistant's shared Modbus connection
   ([developer docs](https://developers.home-assistant.io/docs/modbus/introduction/),
   [background](https://developers.home-assistant.io/blog/2026/07/05/modernizing-modbus/)), in the style of
   [trovis-modbus](https://github.com/Tom-Bom-badil/trovis-modbus).
3. A HACS integration with a config flow (host, port, unit id, application), and later a Home Assistant core
   contribution once that Modbus API has settled.

## License

MIT, see [LICENSE](LICENSE). Danfoss, ECL Comfort and Leanheat are trademarks of their owners. This project is not
affiliated with Danfoss.
