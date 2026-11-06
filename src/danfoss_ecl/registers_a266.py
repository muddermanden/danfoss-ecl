"""A266 register catalog.

Settings come from the Operating Guide appendix *Parameter ID overview*
(factory, range, A266.x, Parameter Name). Live/output/ident PNUs come from
the communication description. Wire metadata (scale, signed, encoding) is
not in the appendix.

Modbus address = PNU − 1.
Source strings (group/name/title/description) are English gettext msgids.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Kind = Literal["setting", "live", "output", "ident"]
Poll = Literal["fast", "slow", "once"]
Factory = int | float | str | None

ALL = ("1", "2", "9", "10")
A12 = ("1", "2")
A2 = ("2",)
A9 = ("9",)
A910 = ("9", "10")
A2910 = ("2", "9", "10")
A1210 = ("1", "2", "10")
NONE = ()  # PNU exists on the wire for some keys, not used on A266.1


@dataclass(frozen=True)
class Variant:
    """One appendix row. `-||-` in the guide becomes extra variants."""

    subtypes: tuple[str, ...]
    vmin: float | None = None
    vmax: float | None = None
    off: float | None = None
    choices: tuple[str, ...] | None = None
    factory: Factory = None
    unit: str = ""

    def a266_text(self) -> str:
        return ", ".join(self.subtypes)


@dataclass(frozen=True)
class Register:
    group: str
    name: str
    pnu: int
    kind: Kind = "setting"
    scale: int = 1
    signed: bool = False
    encoding: str = "scaled"
    title: str = ""
    description: str = ""
    guide_page: int | None = None
    poll: Poll | None = None
    variants: tuple[Variant, ...] = ()

    @property
    def poll_group(self) -> Poll:
        if self.poll is not None:
            return self.poll
        mapping: dict[Kind, Poll] = {
            "setting": "slow",
            "live": "fast",
            "output": "fast",
            "ident": "once",
        }
        return mapping[self.kind]

    def variant_for(self, app: str) -> Variant | None:
        for variant in self.variants:
            if app in variant.subtypes:
                return variant
        return None

    def primary_variant(self) -> Variant | None:
        return self.variants[0] if self.variants else None


def V(
    subtypes: tuple[str, ...] = ALL,
    *,
    vmin: float | None = None,
    vmax: float | None = None,
    off: float | None = None,
    choices: tuple[str, ...] | None = None,
    factory: Factory = None,
    unit: str = "",
) -> Variant:
    return Variant(
        subtypes,
        vmin=vmin,
        vmax=vmax,
        off=off,
        choices=choices,
        factory=factory,
        unit=unit,
    )


OFF_ON = ("OFF", "ON")
ABV_GEAR = ("ABV", "GEAR")
STOP_START = ("STOP", "START")
UNITS_FLOW = (
    "ml, l/h",
    "l, l/h",
    "ml, m³/h",
    "l, m³/h",
    "Wh, kW",
    "kWh, kW",
    "kWh, MW",
    "MWh, MW",
    "GWh, GW",
)
INPUT_TYPE = (
    "OFF",
    "IM1",
    "IM2",
    "IM3",
    "IM4",
    "EM1",
    "EM2",
    "EM3",
    "EM4",
    "EM5",
)
INPUT_TYPE_9 = ("EM1", "EM2", "EM3", "EM4", "EM5", "OFF")
EXT_OVERRIDE = (
    "OFF",
    "S1",
    "S2",
    "S3",
    "S4",
    "S5",
    "S6",
    "S7",
    "S8",
    "S9",
    "S10",
    "S11",
    "S12",
    "S13",
    "S14",
    "S15",
    "S16",
)
EXT_MODE_HEAT = ("COMFORT", "SAVING", "FROST PR.", "CONST. T")
EXT_MODE_DHW = ("COMFORT", "SAVING", "FROST PR.")
ECA_ADDR = ("OFF", "A", "B")
BASED_ON = ("OUT", "ROOM")


REGISTERS: list[Register] = [
    # --- live sensors (communication description) ---
    Register(
        "Sensors", "S1 outdoor raw", 10201, kind="live", scale=100, signed=True,
        title="Outdoor temperature",
        description="Pt 1000 outdoor sensor, raw.",
        variants=(V(vmin=-60, vmax=150, unit="°C"),),
    ),
    Register(
        "Sensors", "S2 room raw", 10202, kind="live", scale=100, signed=True,
        title="Room temperature",
        description="Pt 1000 room sensor, raw. 192 °C means the sensor is open.",
        variants=(V(vmin=-60, vmax=150, unit="°C"),),
    ),
    Register(
        "Sensors", "S3 heating flow raw", 10203, kind="live", scale=100, signed=True,
        title="Heating flow temperature",
        description="Pt 1000 heating flow sensor, raw.",
        variants=(V(vmin=-60, vmax=150, unit="°C"),),
    ),
    Register(
        "Sensors", "S4 DHW / tank raw", 10204, kind="live", scale=100, signed=True,
        title="DHW / tank temperature",
        description="Pt 1000 DHW or storage-tank sensor, raw.",
        variants=(V(vmin=-60, vmax=150, unit="°C"),),
    ),
    Register(
        "Sensors", "S5 heating return raw", 10205, kind="live", scale=100, signed=True,
        title="Heating return temperature",
        description="Pt 1000 heating return sensor, raw.",
        variants=(V(vmin=-60, vmax=150, unit="°C"),),
    ),
    Register(
        "Sensors", "S6 DHW return raw", 10206, kind="live", scale=100, signed=True,
        title="DHW return temperature",
        description="Pt 1000 DHW return sensor, raw.",
        variants=(V(vmin=-60, vmax=150, unit="°C"),),
    ),
    Register(
        "Sensors", "S7 raw", 10207, kind="live", scale=100, signed=True,
        title="Sensor S7",
        description="Pt 1000 input S7, raw.",
        variants=(V(vmin=-60, vmax=150, unit="°C"),),
    ),
    Register(
        "Sensors", "S8 raw", 10208, kind="live", scale=100, signed=True,
        title="Sensor S8",
        description="Pt 1000 input S8, raw.",
        variants=(V(vmin=-60, vmax=150, unit="°C"),),
    ),
    Register(
        "Sensors", "S9 raw", 10209, kind="live", scale=100, signed=True,
        title="Sensor S9",
        description="Pt 1000 input S9, raw.",
        variants=(V(vmin=-60, vmax=150, unit="°C"),),
    ),
    Register(
        "Sensors", "S10 raw", 10210, kind="live", scale=100, signed=True,
        title="Sensor S10",
        description="Pt 1000 input S10, raw.",
        variants=(V(vmin=-60, vmax=150, unit="°C"),),
    ),
    Register(
        "Sensors", "S1 circuit view", 11201, kind="live", scale=100, signed=True,
        title="S1 as shown in the circuit display",
        variants=(V(vmin=-60, vmax=150, unit="°C"),),
    ),
    Register(
        "Sensors", "S2 circuit view", 11202, kind="live", scale=100, signed=True,
        title="S2 as shown in the circuit display",
        variants=(V(vmin=-60, vmax=150, unit="°C"),),
    ),
    Register(
        "Sensors", "S3 circuit view", 11203, kind="live", scale=100, signed=True,
        title="S3 as shown in the circuit display",
        description="Not present on A266.1.",
        variants=(V(NONE, vmin=-60, vmax=150, unit="°C"),),
    ),
    Register(
        "Sensors", "S4 circuit view", 11204, kind="live", scale=100, signed=True,
        title="S4 as shown in the circuit display",
        description="Not present on A266.1.",
        variants=(V(NONE, vmin=-60, vmax=150, unit="°C"),),
    ),
    Register(
        "Sensors", "S5 circuit view", 11205, kind="live", scale=100, signed=True,
        title="S5 as shown in the circuit display",
        description="Not present on A266.1.",
        variants=(V(NONE, vmin=-60, vmax=150, unit="°C"),),
    ),
    Register(
        "Sensors", "S6 circuit view", 11206, kind="live", scale=100, signed=True,
        title="S6 as shown in the circuit display",
        description="Not present on A266.1.",
        variants=(V(NONE, vmin=-60, vmax=150, unit="°C"),),
    ),
    Register(
        "Sensors", "S3 desired flow", 11253, kind="live", scale=100, signed=True,
        title="Desired heating flow temperature",
        description="Controller reference for the heating flow. This is what the 3-point valve is chasing.",
        variants=(V(vmin=0, vmax=150, unit="°C"),),
    ),
    Register(
        "Sensors", "S4 desired flow", 11254, kind="live", scale=100, signed=True,
        title="Desired DHW flow temperature",
        description="Not present on A266.1 (storage tank uses S4 as tank sensor).",
        variants=(V(NONE, vmin=0, vmax=150, unit="°C"),),
    ),
    # --- outputs ---
    Register(
        "Outputs", "ECA32 AO1 status %", 4016, kind="output", scale=10,
        title="ECA 32 analogue output 1",
        description="0-10 V status. Not the 3-point gear motor position.",
        variants=(V(vmin=0, vmax=100, unit="%"),),
    ),
    Register(
        "Outputs", "ECA32 AO2 status %", 4017, kind="output", scale=10,
        title="ECA 32 analogue output 2",
        variants=(V(vmin=0, vmax=100, unit="%"),),
    ),
    Register(
        "Outputs", "ECA32 AO3 status %", 4018, kind="output", scale=10,
        title="ECA 32 analogue output 3",
        variants=(V(vmin=0, vmax=100, unit="%"),),
    ),
    Register("Outputs", "Triac 1", 4000, kind="output", title="Triac 1", variants=(V(choices=OFF_ON),)),
    Register("Outputs", "Triac 2", 4001, kind="output", title="Triac 2", variants=(V(choices=OFF_ON),)),
    Register("Outputs", "Triac 3", 4002, kind="output", title="Triac 3", variants=(V(choices=OFF_ON),)),
    Register("Outputs", "Triac 4", 4003, kind="output", title="Triac 4", variants=(V(choices=OFF_ON),)),
    Register("Outputs", "Relay 1", 4006, kind="output", title="Relay 1 (typically heating pump)", variants=(V(choices=OFF_ON),)),
    Register("Outputs", "Relay 2", 4007, kind="output", title="Relay 2 (typically DHW pump)", variants=(V(choices=OFF_ON),)),
    Register("Outputs", "Relay 3", 4008, kind="output", title="Relay 3", variants=(V(choices=OFF_ON),)),
    Register("Outputs", "Relay 4", 4009, kind="output", title="Relay 4", variants=(V(choices=OFF_ON),)),
    Register("Outputs", "Digital output bitmask 3998", 3998, kind="output", title="Digital output bitmask", variants=(V(),)),
    Register("Outputs", "Digital output bitmask 3999", 3999, kind="output", title="Digital output bitmask", variants=(V(),)),
    Register("Operation", "Mode circuit 1", 4201, kind="live", title="Operating mode, heating circuit", variants=(V(),)),
    Register("Operation", "Mode circuit 2", 4202, kind="live", title="Operating mode, DHW circuit", variants=(V(),)),
    Register("Operation", "Status circuit 1", 4211, kind="live", title="Status, heating circuit", variants=(V(),)),
    Register("Operation", "Status circuit 2", 4212, kind="live", title="Status, DHW circuit", variants=(V(),)),
    # --- ident ---
    Register("System", "Modbus address", 38, kind="ident", title="Modbus slave address", variants=(V(vmin=1, vmax=247),)),
    Register(
        "System", "Software version", 35, kind="ident", encoding="majmin",
        title="Controller software version",
        description="Packed as major<<8|minor. 557 is 2.45.",
        variants=(V(),),
    ),
    Register(
        "System", "Hardware revision", 34, kind="ident", encoding="majmin",
        title="Controller hardware revision",
        description="Packed major.minor. Not the production date.",
        variants=(V(),),
    ),
    Register("System", "Software build", 8, kind="ident", title="Software build number", variants=(V(),)),
    Register("System", "Serial high", 36, kind="ident", title="Serial number, high word", variants=(V(),)),
    Register("System", "Serial low", 37, kind="ident", title="Serial number, low word", variants=(V(),)),
    Register(
        "System", "Production week/year", 2099, kind="ident", encoding="year_week",
        title="Production week and year",
        description="High byte = year-2000, low byte = ISO week. Shown as week.year (32.2025).",
        variants=(V(),),
    ),
    Register("System", "Application prefix", 2060, kind="ident", encoding="ascii", title="Application prefix (A)", variants=(V(),)),
    Register("System", "Application type", 2061, kind="ident", title="Application type number (266)", variants=(V(),)),
    Register("System", "Application subtype", 2062, kind="ident", title="Application subtype (.1 / .2 / .9 / .10)", variants=(V(),)),
    Register("System", "Application version", 2063, kind="ident", encoding="majmin", title="Application version", variants=(V(),)),
    # --- Parameter ID overview: floor drying ---
    Register(
        "Floor drying", "Prog. execution", 10512, guide_page=None,
        title="Programme execution",
        description="Floor (screed) drying programme running.",
        variants=(V(choices=OFF_ON, factory="OFF"),),
    ),
    Register(
        "Floor drying", "Max. pwr. failure", 10514, guide_page=None,
        title="Maximum power failure",
        variants=(V(vmin=5, vmax=3000, factory=30, unit="min"),),
    ),
    Register(
        "Floor drying", "Ramp X5-X6", 10903,
        title="Ramp between X5 and X6",
        variants=(V(vmin=1, vmax=20, off=0, factory=5),),
    ),
    Register(
        "Floor drying", "Ramp X7-X8", 10904,
        title="Ramp between X7 and X8",
        variants=(V(vmin=1, vmax=20, off=0, factory=5),),
    ),
    Register(
        "Floor drying", "Appl. continue", 10912,
        title="Application continued",
        variants=(V(choices=OFF_ON, factory="OFF"),),
    ),
    Register(
        "Floor drying", "After power fail.", 10913,
        title="After power failure",
        description="Appendix factory is OFF even though the range is STOP / START.",
        variants=(V(choices=STOP_START, factory="OFF"),),
    ),
    Register("Floor drying", "X1", 10930, title="Screed drying X1", variants=(V(vmin=0, vmax=1200, factory=0, unit="h"),)),
    Register("Floor drying", "X2", 10931, title="Screed drying X2", variants=(V(vmin=0, vmax=1200, factory=0, unit="h"),)),
    Register("Floor drying", "X3", 10932, title="Screed drying X3", variants=(V(vmin=0, vmax=1200, factory=0, unit="h"),)),
    Register("Floor drying", "X4", 10933, title="Screed drying X4", variants=(V(vmin=0, vmax=1200, factory=0, unit="h"),)),
    Register("Floor drying", "X5", 10934, title="Screed drying X5", variants=(V(vmin=0, vmax=1200, factory=0, unit="h"),)),
    Register("Floor drying", "X6", 10935, title="Screed drying X6", variants=(V(vmin=0, vmax=1200, factory=360, unit="h"),)),
    Register("Floor drying", "X7", 10936, title="Screed drying X7", variants=(V(vmin=0, vmax=1200, factory=720, unit="h"),)),
    Register("Floor drying", "X8", 10937, title="Screed drying X8", variants=(V(vmin=0, vmax=1200, factory=1080, unit="h"),)),
    # --- Heating circuit 1 (Parameter ID overview) ---
    Register(
        "Heating", "Desired T", 11004, signed=True, guide_page=73,
        title="Desired flow temperature",
        description="Used in constant-temperature mode.",
        variants=(V(vmin=5, vmax=150, factory=50, unit="°C"),),
    ),
    Register(
        "Heating", "ECA addr.", 11010, guide_page=102,
        title="ECA address, choice of Remote Control Unit",
        description="OFF: no ECA. A or B must match the address set on the remote.",
        variants=(V(A12, choices=ECA_ADDR, factory="OFF"),),
    ),
    Register(
        "Heating", "Auto saving", 11011, signed=True, guide_page=88,
        title="Saving temperature dependent on outdoor temperature",
        variants=(V(vmin=-29, vmax=10, factory=-15, unit="°C"),),
    ),
    Register(
        "Heating", "Boost", 11012, guide_page=89,
        title="Boost",
        description="Temporarily raises desired flow after a saving period. OFF: not active.",
        variants=(V(vmin=1, vmax=99, off=0, factory="OFF", unit="%"),),
    ),
    Register(
        "Heating", "Ramp", 11013, guide_page=90,
        title="Reference ramping",
        description="Desired flow increases gradually to avoid load peaks. OFF: not active.",
        variants=(V(vmin=1, vmax=99, off=0, factory="OFF", unit="min"),),
    ),
    Register(
        "Heating", "Optimizer", 11014, guide_page=90,
        title="Optimizing time constant",
        variants=(V(vmin=10, vmax=59, off=9, factory="OFF"),),
    ),
    Register(
        "Heating", "Adapt. time", 11015, guide_page=75,
        title="Adaptation time",
        description="Room-temperature adaptation. Too low a value can make control unstable.",
        variants=(
            V(A12, vmin=1, vmax=50, off=0, factory="OFF", unit="s"),
            V(A910, vmin=1, vmax=50, off=0, factory=25, unit="s"),
        ),
    ),
    Register(
        "Heating", "Demand offset", 11017, guide_page=102,
        title="Demand offset",
        variants=(V(vmin=1, vmax=20, off=0, factory="OFF", unit="K"),),
    ),
    Register(
        "Heating", "Based on", 11020, guide_page=91,
        title="Optimization based on room / outdoor temperature",
        description="OUT if no room sensor is measured.",
        variants=(V(A12, choices=BASED_ON, factory="OUT"),),
    ),
    Register(
        "Heating", "Total stop", 11021, guide_page=91,
        title="Total stop during saving",
        variants=(V(choices=OFF_ON, factory="OFF"),),
    ),
    Register(
        "Heating", "P exercise", 11022, guide_page=102,
        title="Pump exercise",
        description="Runs the pump 1 minute every third day to avoid seizure.",
        variants=(V(choices=OFF_ON, factory="ON"),),
    ),
    Register(
        "Heating", "M exercise", 11023, guide_page=103,
        title="Valve exercise",
        description="Opens 7 minutes and closes 7 minutes in periods without heat demand.",
        variants=(V(choices=OFF_ON, factory="OFF"),),
    ),
    Register(
        "Heating", "Actuator", 11024, guide_page=96,
        title="Actuator",
        description="ABV: thermo actuator. GEAR: gear motor. GEAR uses M run, Nz, Xp, Tn.",
        variants=(V(choices=ABV_GEAR, factory="GEAR"),),
    ),
    Register(
        "Heating", "Pre-stop", 11026, guide_page=92,
        title="Optimized stop time",
        variants=(V(choices=OFF_ON, factory="ON"),),
    ),
    Register(
        "Heating", "Con. T, ret. T lim.", 11028, signed=True, guide_page=79,
        title="Constant temperature mode, return temperature limitation",
        variants=(V(vmin=10, vmax=110, factory=70, unit="°C"),),
    ),
    Register(
        "Heating", "DHW, ret. T limit", 11029, signed=True, guide_page=79,
        title="DHW return temperature limitation",
        variants=(V(vmin=10, vmax=110, off=9, factory="OFF", unit="°C"),),
    ),
    Register(
        "Heating", "High T out X1", 11031, signed=True, guide_page=80,
        title="Return temp. limitation, high outdoor T, X-axis",
        variants=(V(vmin=-60, vmax=20, factory=15, unit="°C"),),
    ),
    Register(
        "Heating", "Low limit Y1", 11032, signed=True, guide_page=80,
        title="Return temp. limitation, low limit, Y-axis",
        variants=(V(vmin=10, vmax=150, factory=50, unit="°C"),),
    ),
    Register(
        "Heating", "Low T out X2", 11033, signed=True, guide_page=80,
        title="Return temp. limitation, low outdoor T, X-axis",
        variants=(V(vmin=-60, vmax=20, factory=-15, unit="°C"),),
    ),
    Register(
        "Heating", "High limit Y2", 11034, signed=True, guide_page=81,
        title="Return temp. limitation, high limit, Y-axis",
        variants=(V(vmin=10, vmax=150, factory=60, unit="°C"),),
    ),
    Register(
        "Heating", "Infl. - max.", 11035, scale=10, signed=True, guide_page=81,
        title="Return temp. limitation — max. influence",
        variants=(
            V(A12, vmin=-9.9, vmax=9.9, factory=-2.0),
            V(A910, vmin=-9.9, vmax=9.9, factory=0.0),
        ),
    ),
    Register(
        "Heating", "Infl. - min.", 11036, scale=10, signed=True, guide_page=81,
        title="Return temp. limitation — min. influence",
        variants=(V(vmin=-9.9, vmax=9.9, factory=0.0),),
    ),
    Register(
        "Heating", "Adapt. time (return)", 11037, guide_page=81,
        title="Return limitation adaptation time",
        description="OFF: return limitation is not adapted. Too low a value risks unstable control.",
        variants=(V(vmin=1, vmax=50, off=0, factory=25, unit="s"),),
    ),
    Register(
        "Heating", "P post-run", 11040, guide_page=103,
        title="Pump post-run",
        description="0: pump stops immediately. Value: remaining heat in the exchanger is used.",
        variants=(V(vmin=0, vmax=99, factory=3, unit="min"),),
    ),
    Register(
        "Heating", "Parallel operation", 11043, guide_page=92,
        title="Parallel operation",
        description="OFF: DHW and heating independent. Value: heating reduced while DHW is charging.",
        variants=(V(vmin=1, vmax=99, off=0, factory="OFF", unit="K"),),
    ),
    Register(
        "Heating", "P demand", 11050, guide_page=103,
        title="Pump demand",
        variants=(V(choices=OFF_ON, factory="OFF"),),
    ),
    Register(
        "Heating", "DHW priority", 11052, guide_page=104,
        title="DHW priority (closed valve / normal operation)",
        variants=(V(choices=OFF_ON, factory="OFF"),),
    ),
    Register(
        "Heating", "P frost T", 11077, signed=True, guide_page=104,
        title="Circulation pump, frost protection temperature",
        description="Pump is ON when outdoor temperature is below this value. 2 °C is recommended.",
        variants=(V(vmin=-10, vmax=20, factory=2, unit="°C"),),
    ),
    Register(
        "Heating", "P heat T", 11078, signed=True, guide_page=104,
        title="Pump heat demand",
        description="Pump ON when desired flow is above this value. Valve stays closed while the pump is off.",
        variants=(V(vmin=5, vmax=40, factory=20, unit="°C"),),
    ),
    Register(
        "Heating", "Max. flow T", 11079, signed=True, guide_page=114,
        title="Maximum flow temperature alarm",
        variants=(
            V(A2, vmin=10, vmax=110, factory=100, unit="°C"),
            V(A910, vmin=10, vmax=110, factory=90, unit="°C"),
        ),
    ),
    Register(
        "Heating", "Delay", 11080, guide_page=114,
        title="Alarm delay",
        variants=(
            V(A2, vmin=5, vmax=250, factory=30, unit="s"),
            V(A910, vmin=5, vmax=250, factory=60, unit="s"),
        ),
    ),
    Register(
        "Heating", "Priority", 11085, guide_page=82,
        title="Priority for return temp. limitation",
        variants=(V(choices=OFF_ON, factory="OFF"),),
    ),
    Register(
        "Heating", "Frost pr. T", 11093, signed=True, guide_page=105,
        title="Frost protection temperature",
        variants=(V(vmin=5, vmax=40, factory=10, unit="°C"),),
    ),
    Register(
        "Heating", "Input type", 11109, guide_page=84,
        title="Flow / energy meter input type",
        variants=(
            V(A1210, choices=INPUT_TYPE, factory="OFF"),
            V(A9, choices=INPUT_TYPE_9, factory="OFF"),
        ),
    ),
    Register(
        "Heating", "Adapt. time (flow)", 11112, guide_page=84,
        title="Flow / power limitation adaptation time",
        variants=(V(vmin=1, vmax=50, off=0, factory="OFF", unit="s"),),
    ),
    Register(
        "Heating", "Filter constant", 11113, guide_page=85,
        title="Filter constant",
        description="Higher value damps the measured flow/power more.",
        variants=(V(vmin=1, vmax=50, factory=10),),
    ),
    Register(
        "Heating", "Pulse", 11114, guide_page=85,
        title="Pulse value from flow / energy meter",
        variants=(V(vmin=1, vmax=9999, off=0, factory="OFF"),),
    ),
    Register(
        "Heating", "Units", 11115, guide_page=85,
        title="Units for measured values",
        variants=(V(choices=UNITS_FLOW, factory="ml, l/h"),),
    ),
    Register(
        "Heating", "High limit Y2 (flow)", 11116, scale=10, guide_page=86,
        title="Flow / power limitation, high limit, Y-axis",
        variants=(V(vmin=0.0, vmax=999.9, factory=999.9),),
    ),
    Register(
        "Heating", "Low limit Y1 (flow)", 11117, scale=10, guide_page=86,
        title="Flow / power limitation, low limit, Y-axis",
        variants=(V(vmin=0.0, vmax=999.9, factory=999.9),),
    ),
    Register(
        "Heating", "Low T out X2 (flow)", 11118, signed=True, guide_page=86,
        title="Flow / power limitation, low outdoor T, X-axis",
        variants=(V(vmin=-60, vmax=20, factory=-15, unit="°C"),),
    ),
    Register(
        "Heating", "High T out X1 (flow)", 11119, signed=True, guide_page=87,
        title="Flow / power limitation, high outdoor T, X-axis",
        variants=(V(vmin=-60, vmax=20, factory=15, unit="°C"),),
    ),
    Register(
        "Heating", "Ext. input", 11141, guide_page=105,
        title="External override input",
        variants=(V(choices=EXT_OVERRIDE, factory="OFF"),),
    ),
    Register(
        "Heating", "Ext. mode", 11142, guide_page=106,
        title="External override mode",
        description="Only applies when the circuit is in scheduled mode.",
        variants=(V(choices=EXT_MODE_HEAT, factory="COMFORT"),),
    ),
    Register(
        "Heating", "Upper difference", 11147, guide_page=114,
        title="Upper difference (alarm)",
        variants=(V(A12, vmin=1, vmax=30, off=0, factory="OFF", unit="K"),),
    ),
    Register(
        "Heating", "Lower difference", 11148, guide_page=115,
        title="Lower difference (alarm)",
        variants=(V(A12, vmin=1, vmax=30, off=0, factory="OFF", unit="K"),),
    ),
    Register(
        "Heating", "Delay (alarm)", 11149, guide_page=115,
        title="Alarm delay",
        variants=(V(A12, vmin=1, vmax=99, factory=10, unit="min"),),
    ),
    Register(
        "Heating", "Lowest temp.", 11150, signed=True, guide_page=116,
        title="Lowest temperature (cancel alarm)",
        variants=(V(A12, vmin=10, vmax=50, factory=30, unit="°C"),),
    ),
    Register(
        "Heating", "Motor pr.", 11174, guide_page=98,
        title="Motor protection",
        description="Prevents actuator oscillation at very low load. Increases lifetime of valve and motor.",
        variants=(V(vmin=10, vmax=59, off=9, factory="OFF", unit="min"),),
    ),
    Register(
        "Heating", "Heat curve", 11175, scale=10, signed=True, guide_page=72,
        title="Heat curve slope",
        description="Not listed in Parameter ID overview. Weather-compensation slope.",
        variants=(V(vmin=0.1, vmax=4.0, unit=""),),
    ),
    Register(
        "Heating", "Temp. min.", 11177, signed=True, guide_page=74,
        title="Minimum flow temperature",
        description="Desired flow will not go below this. Has higher priority than the heat curve.",
        variants=(V(vmin=10, vmax=150, factory=10, unit="°C"),),
    ),
    Register(
        "Heating", "Temp. max.", 11178, signed=True, guide_page=74,
        title="Maximum flow temperature",
        description="Desired flow will not go above this.",
        variants=(V(vmin=10, vmax=150, factory=90, unit="°C"),),
    ),
    Register(
        "Heating", "Summer, cut-out", 11179, signed=True, guide_page=93,
        title="Limit for heating cut-out",
        description="Heating is switched off when outdoor temperature is higher than this.",
        variants=(V(vmin=1, vmax=50, off=0, factory=20, unit="°C"),),
    ),
    Register(
        "Heating", "Desired room comfort", 11180, scale=10, signed=True,
        title="Desired room temperature, comfort",
        description="Not listed in Parameter ID overview. Comfort setpoint on the daily display.",
        variants=(V(vmin=5.0, vmax=40.0, unit="°C"),),
    ),
    Register(
        "Heating", "Desired room saving", 11181, scale=10, signed=True,
        title="Desired room temperature, saving",
        description="Not listed in Parameter ID overview.",
        variants=(V(vmin=5.0, vmax=40.0, unit="°C"),),
    ),
    Register(
        "Heating", "Infl. - max. (room)", 11182, scale=10, signed=True, guide_page=75,
        title="Room temp. limitation, max. influence",
        variants=(V(vmin=-9.9, vmax=0.0, factory=-4.0),),
    ),
    Register(
        "Heating", "Infl. - min. (room)", 11183, scale=10, signed=True, guide_page=76,
        title="Room temp. limitation, min. influence",
        variants=(V(vmin=0.0, vmax=9.9, factory=0.0),),
    ),
    Register(
        "Heating", "Xp", 11184, guide_page=98,
        title="Proportional band",
        description="Higher value: slower, more stable flow-temperature control.",
        variants=(V(vmin=5, vmax=250, factory=120, unit="K"),),
    ),
    Register(
        "Heating", "Tn", 11185, guide_page=99,
        title="Integration time constant",
        description="High value: slow but stable. Low value: fast, less stable.",
        variants=(V(vmin=1, vmax=999, factory=50, unit="s"),),
    ),
    Register(
        "Heating", "M run", 11186, guide_page=99,
        title="Running time of the motorized control valve",
        description="Seconds from fully closed to fully open. Measure with a stopwatch, or stroke x actuator speed. Too short a time keeps the motor driving in end stop.",
        variants=(V(vmin=5, vmax=250, factory=60, unit="s"),),
    ),
    Register(
        "Heating", "Nz", 11187, guide_page=99,
        title="Neutral zone",
        description="When actual flow is within this zone the controller does not activate the valve. Symmetrical around the desired flow. Set high if you can accept more variation.",
        variants=(V(vmin=1, vmax=9, factory=3, unit="K"),),
    ),
    Register(
        "Heating", "Min. act. time", 11189, guide_page=99,
        title="Min. activation time, gear motor",
        description="Keep as high as acceptable to increase actuator lifetime. Unit is 20 ms steps (10 = 200 ms).",
        variants=(V(vmin=2, vmax=50, factory=10),),
    ),
    Register(
        "Heating", "Sum. start, month", 11392, guide_page=111,
        title="Summer cut-out start, month",
        variants=(V(vmin=1, vmax=12, factory=5),),
    ),
    Register(
        "Heating", "Sum. start, day", 11393, guide_page=111,
        title="Summer cut-out start, day",
        variants=(V(vmin=1, vmax=31, factory=20),),
    ),
    Register(
        "Heating", "Summer, filter", 11395, guide_page=111,
        title="Summer filter",
        variants=(V(vmin=1, vmax=300, off=0, factory=250),),
    ),
    Register(
        "Heating", "Win. start, month", 11396, guide_page=111,
        title="Winter cut-out start, month",
        variants=(V(vmin=1, vmax=12, factory=5),),
    ),
    Register(
        "Heating", "Winter start, day", 11397, guide_page=111,
        title="Winter cut-out start, day",
        variants=(V(vmin=1, vmax=31, factory=20),),
    ),
    Register(
        "Heating", "Winter, cut-out", 11398, signed=True, guide_page=111,
        title="Winter cut-out temperature",
        variants=(V(vmin=1, vmax=50, off=0, factory=20, unit="°C"),),
    ),
    Register(
        "Heating", "Winter, filter", 11399, guide_page=111,
        title="Winter filter",
        variants=(V(vmin=1, vmax=300, off=0, factory=250),),
    ),
    Register(
        "Heating", "Send desired T", 11500, guide_page=108,
        title="Send desired T",
        description="ON: this circuit sends its desired flow to a master controller.",
        variants=(V(choices=OFF_ON, factory="ON"),),
    ),
    Register(
        "Heating", "Pressure", 11600, signed=True,
        title="Pressure",
        variants=(V(A9, vmin=-7.8125, vmax=7.8125, factory=0.0, unit="bar"),),
    ),
    Register("Heating", "Low X", 11607, scale=10, guide_page=116, title="Pressure input, low X (voltage)", variants=(V(A9, vmin=0.0, vmax=10.0, factory=1.0),)),
    Register("Heating", "High X", 11608, scale=10, guide_page=116, title="Pressure input, high X (voltage)", variants=(V(A9, vmin=0.0, vmax=10.0, factory=5.0),)),
    Register("Heating", "Low Y", 11609, scale=10, guide_page=116, title="Pressure input, low Y (bar)", variants=(V(A9, vmin=0.0, vmax=10.0, factory=0.0),)),
    Register("Heating", "High Y", 11610, scale=10, guide_page=117, title="Pressure input, high Y (bar)", variants=(V(A9, vmin=0.0, vmax=10.0, factory=6.0),)),
    Register("Heating", "Alarm high", 11614, scale=10, guide_page=117, title="Pressure alarm high", variants=(V(A9, vmin=0.0, vmax=6.0, factory=2.3),)),
    Register("Heating", "Alarm low", 11615, scale=10, guide_page=117, title="Pressure alarm low", variants=(V(A9, vmin=0.0, vmax=6.0, factory=0.8),)),
    Register("Heating", "Alarm time-out", 11617, guide_page=117, title="Pressure alarm time-out", variants=(V(A9, vmin=0, vmax=240, factory=30, unit="s"),)),
    Register("Heating", "Digital", 11623, title="Digital alarm input", variants=(V(A910, vmin=0, vmax=1, factory=0),)),
    Register("Heating", "Alarm value", 11636, guide_page=117, title="Digital alarm value", variants=(V(A910, vmin=0, vmax=1, factory=1),)),
    Register("Heating", "Alarm time-out (digital)", 11637, guide_page=118, title="Digital alarm time-out", variants=(V(A910, vmin=0, vmax=240, factory=30, unit="s"),)),
    Register(
        "Heating", "Circuit, Estrich.", 11910,
        title="Screed drying circuit",
        variants=(V(choices=OFF_ON, factory="ON"),),
    ),
    # --- DHW circuit 2 ---
    Register(
        "DHW", "P exercise", 12022, guide_page=102,
        title="Pump exercise",
        variants=(
            V(A12, choices=OFF_ON, factory="OFF"),
            V(A910, choices=OFF_ON, factory="ON"),
        ),
    ),
    Register(
        "DHW", "M exercise", 12023, guide_page=103,
        title="Valve exercise",
        variants=(V(choices=OFF_ON, factory="OFF"),),
    ),
    Register(
        "DHW", "Actuator", 12024, guide_page=96,
        title="Actuator",
        description="ABV: thermo actuator. GEAR: gear motor.",
        variants=(V(choices=ABV_GEAR, factory="GEAR"),),
    ),
    Register(
        "DHW", "Limit", 12030, signed=True, guide_page=80,
        title="Return temperature limitation",
        variants=(V(vmin=10, vmax=120, factory=60, unit="°C"),),
    ),
    Register(
        "DHW", "Infl. - max.", 12035, scale=10, signed=True, guide_page=81,
        title="Return temp. limitation — max. influence",
        variants=(
            V(A12, vmin=-9.9, vmax=9.9, factory=-2.0),
            V(A910, vmin=-9.9, vmax=9.9, factory=0.0),
        ),
    ),
    Register(
        "DHW", "Infl. - min.", 12036, scale=10, signed=True, guide_page=81,
        title="Return temp. limitation — min. influence",
        variants=(V(vmin=-9.9, vmax=9.9, factory=0.0),),
    ),
    Register(
        "DHW", "Adapt. time", 12037, guide_page=81,
        title="Return limitation adaptation time",
        variants=(V(vmin=1, vmax=50, off=0, factory=25, unit="s"),),
    ),
    Register(
        "DHW", "P post-run", 12040, guide_page=103,
        title="Pump post-run",
        variants=(V(vmin=0, vmax=99, factory=3, unit="min"),),
    ),
    Register(
        "DHW", "P frost T", 12077, signed=True, guide_page=104,
        title="Circulation pump, frost protection temperature",
        variants=(V(vmin=-10, vmax=20, factory=2, unit="°C"),),
    ),
    Register(
        "DHW", "P heat T", 12078, signed=True, guide_page=104,
        title="Pump heat demand",
        variants=(V(vmin=5, vmax=80, factory=20, unit="°C"),),
    ),
    Register(
        "DHW", "Priority", 12085, guide_page=82,
        title="Priority for return temp. limitation",
        variants=(V(A12, choices=OFF_ON, factory="OFF"),),
    ),
    Register(
        "DHW", "Frost pr. T", 12093, signed=True, guide_page=105,
        title="Frost protection temperature",
        variants=(V(vmin=5, vmax=40, factory=10, unit="°C"),),
    ),
    Register(
        "DHW", "Open time", 12094, scale=10, guide_page=96,
        title="Open time (thermo actuator)",
        variants=(V(A2, vmin=0.1, vmax=25.0, off=0, factory=4.0, unit="s"),),
    ),
    Register(
        "DHW", "Close time", 12095, scale=10, guide_page=97,
        title="Close time (thermo actuator)",
        variants=(V(A2, vmin=0.1, vmax=25.0, off=0, factory=2.0, unit="s"),),
    ),
    Register(
        "DHW", "Tn (idle)", 12096, guide_page=97,
        title="Integration time when no DHW tapping",
        variants=(V(A2, vmin=1, vmax=999, factory=120, unit="s"),),
    ),
    Register(
        "DHW", "Supply T (idle)", 12097, guide_page=97,
        title="Supply T (idle)",
        variants=(V(A2, choices=OFF_ON, factory="OFF"),),
    ),
    Register(
        "DHW", "Input type", 12109, guide_page=84,
        title="Flow / energy meter input type",
        variants=(
            V(A1210, choices=INPUT_TYPE, factory="OFF"),
            V(A9, choices=INPUT_TYPE_9, factory="OFF"),
        ),
    ),
    Register(
        "DHW", "Limit (flow)", 12111, scale=10, guide_page=84,
        title="Limitation value",
        variants=(V(vmin=0.0, vmax=999.9, factory=999.9),),
    ),
    Register(
        "DHW", "Adapt. time (flow)", 12112, guide_page=84,
        title="Flow / power limitation adaptation time",
        variants=(V(vmin=1, vmax=50, off=0, factory="OFF", unit="s"),),
    ),
    Register(
        "DHW", "Filter constant", 12113, guide_page=85,
        title="Filter constant",
        variants=(V(vmin=1, vmax=50, factory=10),),
    ),
    Register(
        "DHW", "Pulse", 12114, guide_page=85,
        title="Pulse value from flow / energy meter",
        variants=(V(vmin=1, vmax=9999, off=0, factory="OFF"),),
    ),
    Register(
        "DHW", "Units", 12115, guide_page=85,
        title="Units for measured values",
        variants=(V(choices=UNITS_FLOW, factory="ml, l/h"),),
    ),
    Register(
        "DHW", "Day", 12122, guide_page=120,
        title="Anti-bacteria, day bitmask",
        variants=(V(vmin=0, vmax=127, factory=0),),
    ),
    Register(
        "DHW", "Start time", 12123, guide_page=120,
        title="Anti-bacteria, start time",
        variants=(V(vmin=0, vmax=47, factory=0),),
    ),
    Register(
        "DHW", "Duration", 12124, guide_page=121,
        title="Anti-bacteria duration",
        variants=(V(vmin=10, vmax=600, factory=120, unit="min"),),
    ),
    Register(
        "DHW", "Desired T", 12125, signed=True, guide_page=121,
        title="Anti-bacteria desired DHW temperature",
        description="OFF: anti-bacteria function is not active.",
        variants=(V(vmin=10, vmax=110, off=9, factory="OFF", unit="°C"),),
    ),
    Register(
        "DHW", "Ext. input", 12141, guide_page=105,
        title="External override input",
        variants=(V(choices=EXT_OVERRIDE, factory="OFF"),),
    ),
    Register(
        "DHW", "Ext. mode", 12142, guide_page=106,
        title="External override mode",
        variants=(V(choices=EXT_MODE_DHW, factory="COMFORT"),),
    ),
    Register(
        "DHW", "Upper difference", 12147, guide_page=114,
        title="Upper difference (alarm)",
        variants=(V(A12, vmin=1, vmax=30, off=0, factory="OFF", unit="K"),),
    ),
    Register(
        "DHW", "Lower difference", 12148, guide_page=115,
        title="Lower difference (alarm)",
        variants=(V(A12, vmin=1, vmax=30, off=0, factory="OFF", unit="K"),),
    ),
    Register(
        "DHW", "Delay", 12149, guide_page=115,
        title="Alarm delay",
        variants=(V(A12, vmin=1, vmax=99, factory=10, unit="min"),),
    ),
    Register(
        "DHW", "Lowest temp.", 12150, signed=True, guide_page=116,
        title="Lowest temperature (cancel alarm)",
        variants=(V(A12, vmin=10, vmax=50, factory=30, unit="°C"),),
    ),
    Register(
        "DHW", "Auto tuning", 12173, guide_page=97,
        title="Auto tuning",
        description="When ON, Xp, Tn and M run are set automatically. Nz must still be set. Takes up to 25 minutes.",
        variants=(V(choices=OFF_ON, factory="OFF"),),
    ),
    Register(
        "DHW", "Motor pr.", 12174, guide_page=98,
        title="Motor protection",
        variants=(V(vmin=10, vmax=59, off=9, factory="OFF", unit="min"),),
    ),
    Register(
        "DHW", "Temp. min.", 12177, signed=True, guide_page=74,
        title="Minimum DHW / tank temperature",
        variants=(
            V(A12, vmin=10, vmax=150, factory=10, unit="°C"),
            V(A910, vmin=10, vmax=150, factory=45, unit="°C"),
        ),
    ),
    Register(
        "DHW", "Temp. max.", 12178, signed=True, guide_page=74,
        title="Maximum DHW / tank temperature",
        variants=(
            V(A12, vmin=10, vmax=150, factory=90, unit="°C"),
            V(A910, vmin=10, vmax=150, factory=65, unit="°C"),
        ),
    ),
    Register(
        "DHW", "Xp", 12184, guide_page=98,
        title="Proportional band",
        variants=(
            V(A12, vmin=5, vmax=250, factory=40, unit="K"),
            V(A910, vmin=5, vmax=250, factory=90, unit="K"),
        ),
    ),
    Register(
        "DHW", "Tn", 12185, guide_page=99,
        title="Integration time constant",
        variants=(
            V(A12, vmin=1, vmax=999, factory=20, unit="s"),
            V(A910, vmin=1, vmax=999, factory=13, unit="s"),
        ),
    ),
    Register(
        "DHW", "M run", 12186, guide_page=99,
        title="Running time of the motorized control valve",
        description="Seconds from fully closed to fully open. Factory is 20 s on A266.1 (heating circuit is 60 s).",
        variants=(
            V(A12, vmin=5, vmax=250, factory=20, unit="s"),
            V(A910, vmin=5, vmax=250, factory=15, unit="s"),
        ),
    ),
    Register(
        "DHW", "Nz", 12187, guide_page=99,
        title="Neutral zone",
        description="When actual temperature is within this zone the controller does not activate the valve.",
        variants=(V(vmin=1, vmax=9, factory=3, unit="K"),),
    ),
    Register(
        "DHW", "Min. act. time", 12189, guide_page=99,
        title="Min. activation time, gear motor",
        variants=(
            V(A12, vmin=2, vmax=50, factory=3),
            V(A910, vmin=2, vmax=50, factory=10),
        ),
    ),
    Register(
        "DHW", "Desired DHW comfort", 12190, scale=10, signed=True,
        title="Desired DHW temperature, comfort",
        description="Not listed in Parameter ID overview. Comfort setpoint on the daily display.",
        variants=(V(vmin=10.0, vmax=110.0, unit="°C"),),
    ),
    Register(
        "DHW", "Desired DHW saving", 12191, scale=10, signed=True,
        title="Desired DHW temperature, saving",
        description="Not listed in Parameter ID overview.",
        variants=(V(vmin=10.0, vmax=110.0, unit="°C"),),
    ),
    Register(
        "DHW", "Send desired T", 12500, guide_page=108,
        title="Send desired T",
        variants=(V(choices=OFF_ON, factory="ON"),),
    ),
]
