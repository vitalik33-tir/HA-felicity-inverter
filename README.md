# Felicity Inverter

Custom Home Assistant integration for Felicity inverter WiFi telemetry over the local TCP interface on port `53970`.

This fork is aimed at making the decoder easier to understand and easier to verify against the decompiled app. The integration remains usable in Home Assistant, but reverse-engineered decoding correctness is the primary goal of the project.

The integration polls these commands:

- `wifilocalMonitor:get dev real infor`
- `wifilocalMonitor:get dev basice infor`
- `wifilocalMonitor:get dev set infor`

The inverter may return multiple JSON objects concatenated together with no separators. The integration now splits and parses those payloads safely, keeps the inverter packet (`Type: 80`) as the primary device identity, and preserves BMS packets (`Type: 112`) separately for battery diagnostics.

## Features

- Config flow with **IP**, **port**, and **scan interval**
- Default polling interval: **5 seconds**
- TCP polling with automatic retry on the next cycle if a request fails
- Clean normalized telemetry for Home Assistant sensors
- Decoder structure that separates transport, normalization, and reverse-engineered mapping rules
- CSV-aligned runtime mapping for inverter and BMS payloads
- Energy Dashboard compatible power sensors
- Source-backed aggregate power decoding ported from the app's `TimeDataConnEntity`
- PV string sensors and AC-side layout diagnostics kept separate from source-backed totals
- BMS summary and limit diagnostics
- BMS voltage-extrema diagnostics with explicit cell index values
- Diagnostic device metadata and raw status-code sensors
- Optional raw JSON diagnostic sensor disabled by default

## Decoder Docs

- [Architecture](docs/architecture.md)
- [Decoding Notes](docs/decoding.md)

## Installation

### HACS

1. Open **HACS → Integrations → Custom repositories**
2. Add `https://github.com/vitalik33-tir/HA-felicity-inverter`
3. Select **Integration**
4. Install the repository and restart Home Assistant
5. Add **Felicity Inverter** from **Settings → Devices & services**

### Manual

Copy `custom_components/felicity_inverter` into your Home Assistant `config/custom_components/` directory and restart Home Assistant.

## Configuration

Add the integration from the UI and configure:

- **Name**
- **Host / IP**
- **Port** (default: `53970`)
- **Scan interval** in seconds (default: `5`)

Host, port, and scan interval can also be changed later in the integration options.

## Sensor groups

The integration exposes normalized sensors in these groups:

- **Battery**
  - SOC, voltage, current, signed power
  - charge / discharge power
  - charge / discharge current
  - charge stage
  - battery temperature
- **PV**
  - total voltage, current, power
  - PV1 / PV2 / PV3 voltage, current, power when exposed by the inverter
- **Grid**
  - voltage, current, frequency
  - active power, apparent power, total power
  - import power, export power
- **Load**
  - voltage, current, frequency
  - active power, apparent power, total power
- **Generator**
  - voltage, current, frequency
  - active power, apparent power, total power
- **Smart Load**
  - voltage, current, frequency
  - active power, apparent power, total power
- **Persistent Derived Energy**
  - grid import / export total energy
  - battery charge / discharge total energy
  - generator total energy
  - smart-load total energy
- **System**
  - inverter mode
  - inverter mode raw
  - bus voltage
  - bus negative voltage
  - load percent
- **Temperature**
  - inverter temperature
  - transformer temperature
  - heatsink temperature
  - ambient temperature
  - battery temperature
- **Diagnostic Energy Counters**
  - daily / monthly / yearly / total PV yield
  - daily / monthly / yearly / total load consumption
- **Warnings / Faults**
  - warning code
  - fault code
  - matching binary sensors
- **BMS Diagnostics**
  - BMS firmware, serial, inverter serial, and Modbus address
  - pack voltage, current, SOC, SOH, capacity
  - charge / discharge voltage limits
  - charge / discharge current limits
  - max / min cell voltage and max / min cell index summary values
  - communication, registration, and global status raw values
- **Diagnostics**
  - device serial
  - WiFi serial
  - decoder profile
  - firmware version
  - device software version
  - device hardware version
  - raw inverter and status codes where app labels have not been recovered yet
  - raw JSON payload sensor (disabled by default)

## Energy Dashboard

This integration exposes real-time power sensors for:

- `pv_power`
- `grid_import_power`
- `grid_export_power`
- `load_power`
- `battery_charge_power`
- `battery_discharge_power`

The integration also exposes persistent derived total-energy sensors for grid import/export, battery charge/discharge, generator, and smart-load energy. Those totals are accumulated locally from the source-backed power sensors and persisted across Home Assistant restarts.

Where native inverter counters are trustworthy, the integration prefers them. Where they are not yet proven, persistent energy is derived from source-backed decoded power sensors rather than raw voltage and current values.

That means the likely persistent-energy split is:

- native counters for PV yield and load consumption
- integration-managed persistent totals for grid import/export, battery charge/discharge, generator, and smart-load energy until direct native counters are proven

The inverter `Energy[][]` counters are exposed conservatively. Stable diagnostic counters currently cover only PV yield and load consumption. Candidate mappings for grid export and battery charge / discharge remain available in `energy_decoder_status.inferred_rows`, and unverified rows remain available in raw diagnostics instead of being exported as stable sensor families.

`pFlow` is treated as a raw UI power-flow status bitmask, not as an energy counter.

## Debug logging

```yaml
logger:
  default: info
  logs:
    custom_components.felicity_inverter: debug
```

## Notes

- If TCP communication fails, entities become unavailable until the next successful poll.
- Aggregate PV, grid, load, generator, and smart-load power now follow the subtype-aware branches recovered from `TimeDataConnEntity`.
- Battery voltage and current prefer the BMS `BattList` values when a BMS packet is present, and battery power follows `SocDataRootEntity.batteryPower()` using those BMS values. Inverter-side EMS power remains the fallback when no BMS packet is available.
- `bCStat` charge stage is now exposed directly as `battery_charge_stage` using normalized HA-friendly labels `0=Idle`, `1=Bulk`, `2=Absorption`, `3=Float`, while the existing battery charge status still prefers live BMS charging state when that state is present.
- `workM` now also exposes a labeled `inverter_mode` sensor using normalized operating-mode labels `0=Power On`, `1=Standby`, `2=Bypass`, `3=Battery`, `4=Fault`, `5=Grid`, `6=Charging`. The raw `inverter_mode_raw` code remains available for diagnostics.
- App-side packet handling is now known to use serial-keyed cache composition plus multipart `ttlPack/index` tracking; the integration mirrors the serial-key merge behavior even though the app's internal cache buckets do not map one-to-one to the repo's `real` / `basic` / `set` abstraction.
- Decoder profile diagnostics now expose the broader type/subtype families proven in `ProductPackageDetail` instead of only a single hard-coded profile.
- Persistent derived energy totals use trapezoidal integration over the source-backed power sensors and discard oversized sampling gaps so reconnects or outages do not backfill unobserved energy.
- Some per-channel PV and AC voltage/current/frequency sensors still rely on observed matrix layouts because the direct raw-to-field mapper for those flattened DTO fields has not yet been recovered.
- Estimated power-flow breakdown sensors were removed rather than kept as if they were source-backed.
- No broader app-side label builder was recovered beyond `bCStat`; inverter mode is now exposed from the confirmed `workM` enum, while other remaining status fields stay raw numeric codes until matching source-backed label logic is found.
- Some inverter `Energy[][]` counters are still conservative or provisional until the raw row semantics are proven directly in the decompiled sources.
- The raw JSON sensor is diagnostic only and disabled by default to avoid unnecessary state growth.
