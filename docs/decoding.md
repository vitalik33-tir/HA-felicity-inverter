# Decoding Notes

This document tracks what is confirmed from the decompiled app and what is still conservative.

## Evidence Tiers

### Authoritative Local Decode Sources

- `TimeDataConnEntity` for local runtime array layout and subtype-aware live power extraction
- `SocDataRootEntity` for BMS scales and `Bstate` semantics

### Naming Validation Sources

- `DataTimeRealRootEntity`
- `DataEnergyRootEntity`
- `EnergyDataRootEntity`
- `StorageRealtimeData`
- `TimeDataBaseEntity`

These flattened classes help validate names, but they do not by themselves prove raw array row and column positions.

## Payload Normalization

The decompiled base parser in `f2/t.java` performs a small amount of JSON normalization before downstream code sees a payload.

- If `Energy` is absent and `Energy3` is present, it aliases `Energy3` to `Energy`.
- It normalizes `modID` and `ModAddr` to the same value.
- When `M1SwVer` or `M2SwVer` is present, version-like fields with the sentinel value `65535` are cleared to an empty string.

This is useful parser behavior to mirror, but it still does not provide a definitive row-name mapping for the `Energy[][]` matrix.

## Confirmed BMS Semantics

- `BattList` voltage is scaled by `1/1000`
- `BattList` current is scaled by `1/10`
- `SocDataRootEntity.batteryPower()` multiplies those scaled BMS voltage and current values and rounds the result to 2 decimal places
- `BatsocList` SOC is scaled by `1/100`
- `BatsocList` capacity is scaled by `1/1000`
- `Bstate` bit 13 indicates charging
- `Bstate` bits 12 or 13 indicate the BMS is active

## Realtime Power Decode Status

`TimeDataConnEntity` does contain authoritative subtype-aware methods for the live aggregate power values. Those methods are now the preferred evidence source for these fields:

- `pv_total_power` via `pvPowerBigDecimal(...)`
- `grid_power` via `acTtlInPowerBigDecimal(...)`
- `load_power` via `acTotalOutActPowerBigDecimal(...)`
- `generator_power` via `genPowerPowerBigDecimal(...)`
- `smart_load_power` via `smartLoadTotalPowerBigDecimal(...)`
- `battery_power` via `SocDataRootEntity.batteryPower()` when `BattList` is present, with `TimeDataConnEntity.emsPowerBigDecimal(...)` kept as the fallback when no BMS packet is available

Important consequences from the recovered methods:

- The app uses model-specific branches for `IVEM6048_V1`, `IVEM_V1`, `IVEM4024V1`, 8K families, 20K, 50K, and several other variants.
- The old generic "frequency row versus power row" heuristic is not authoritative for aggregate power.
- The app has a separate BMS-side battery-power formula, so battery voltage/current and battery power should not be treated as inverter-only fields when a BMS packet is present.
- `totalOutPutPowerDecimal()` explicitly reads `ACout[2][4]`, but that slot is often absent in captured payloads, so the integration falls back to active output power when the direct total slot is missing.

What is still not directly proven from the local raw-array decoder:

- per-string PV voltage/current/power placement
- AC-side per-phase current/frequency/apparent-power placement beyond the specific aggregate methods above

Those fields remain useful, but they should be treated as observed layout extracts rather than app-proven raw-to-field mappings.

## Flow Calculations

The app does expose flow-direction helpers such as:

- `linerPVToInt(...)`
- `linerGridEnergyFlow(...)`
- `linerBatteryEnergyFlow(...)`
- `linerBackEnergyFlow(...)`
- `linerLampEnergyFlow(...)`
- `linerGenEnergyFlow(...)`

These helpers do not recover hidden per-link watt values. They compute arrow direction from the same aggregate power methods plus thresholds and sign tests.

That means fields such as:

- PV to load
- PV to battery
- PV to grid
- battery to load
- grid to load
- self consumption
- battery roundtrip efficiency

were local integration estimates, not source-backed app decodes. They have been removed rather than kept as if they were authoritative.

## Selection And Merge Status

The parser normalization in `f2/t.java` is source-backed:

- `Energy3` is aliased to `Energy`
- `modID` and `ModAddr` are harmonized
- synthetic BMS-like `DevSN` values are created from `InvSN` plus Modbus address when needed

`o5/h0.java` and `e2/n.java` now make the app-side merge model much clearer:

- the app keeps multiple serial-keyed caches for different payload families
- cache reads such as `F(str)`, `X(str)`, and `e0(str)` compose JSON fragments by device serial
- multipart payloads are tracked in a dedicated fragment map keyed by serial, with `ttlPack` / `index` checked by `o0()` before some downstream refreshes continue
- `h0.L0()` rebuilds device views by combining those serial-keyed cache entries rather than by trusting a single packet in isolation

Current integration status:

- parser normalization is source-backed
- inverter/BMS merge selection is serial-based and now consistent with the app's recovered serial-key cache composition model

What is still not fully reduced to a one-to-one proof is the exact correspondence between the app's internal cache buckets and this repo's `real` / `basic` / `set` polling abstraction. The integration therefore matches the recovered serial-key join behavior without claiming that every app cache name has been mapped exactly.

## Enum And Label Status

Two currently used label maps are now treated as confirmed in the integration, with user-facing labels normalized to clearer English rather than copied literally from app wording:

- `bcStatus` / `bCStat` fallback stages in `DataTimeRealRootEntity.getInverterStatus()`:
	- `0` = idle
	- `1` = bulk
	- `2` = absorption
	- `3` = float

- `workM` working mode enum:
	- `0` = power on
	- `1` = standby
	- `2` = bypass
	- `3` = battery
	- `4` = fault
	- `5` = grid
	- `6` = charging

The integration now exposes those mappings as `battery_charge_stage` and `inverter_mode`. The existing `battery_charge_status` sensor still prefers live BMS charging state when `Bstate` is available, because that state is closer to instantaneous direction than the inverter's fallback stage enum. The raw `inverter_mode_raw` field remains exposed alongside the mapped `inverter_mode` label.

Other local label maps previously exposed by the integration were not recovered from authoritative app-side label builders in this source pass, including:

- WiFi status text
- BMS communication / registration / global label text
- charge-source priority label text
- smart-port label text
- system-power label text

Those fields are now exposed as raw numeric codes instead of guessed user-facing labels.

Negative findings from this source pass:

- `DataTimeRealRootEntity.fieldFormatLabel(...)` is only a null/empty formatter, not a hidden label decoder
- no separate setter-based mapper into `StorageRealtimeData` was recovered from the accessible source tree
- `DataTimeRealRootEntity` itself does not appear to be the primary local realtime raw-array mapper

Additional mode-related observations from the decompiled app:

- `DataTimeRealRootEntity.getWorkMode()` returns the stored work mode string directly rather than translating it locally
- device-time UI code can display a higher-level `workModeStr` when that field is present in JSON
- `DeviceBaseEntity.canSelfTest()` explicitly allows self-test only when `workMode` is `2` or `5`
- `TimeDataConnEntity` branches on `workM` values for some families, including `3`, `4`, and `5`, which matches the repo's mode-aware grid-power handling

Additional mapper details recovered from `TimeDataConnEntity`:

- `isGridHigh(...)` directly checks `ACin[0][0]`, `ACin[0][1]`, and `ACin[0][2]` against AC-input voltage thresholds, which confirms that at least some models carry explicit per-phase ACin voltage slots in the raw matrix
- `meterPowerBigDecimal(...)` reads from `Home[0][0]` or `Home[1][0..1]` on high-power families, so the `Home` matrix is an active local decode source rather than dead DTO baggage
- `battery1BigDecimal(...)` and `battery2BigDecimal(...)` switch between `Batsoc` / `Batsoc2` and `Batt2` / `Batt`-backed communication-battery lists, which confirms direct pack-slot selection logic even though the integration does not yet expose separate battery-1 / battery-2 sensors

These findings still do not amount to a general flattened DTO mapper for every per-channel UI field. They prove specific row/column consumers, not a complete raw-to-field assignment for all per-string PV and AC detail values.

## Profile Handling

`ProductPackageDetail` proves that the app does not use a single generic realtime decoder. It gates branches on many type/subtype checks such as:

- `isCheckDeviceIVEM6048_V1()`
- `isCheckDeviceIVEM_V1()`
- `isCheckDeviceIVEM4024V1()`
- `isCheckDevice8K()`
- `isCheckDevice20K()`
- `isCheckDevice50K()`
- `isCheckDeviceIVPM()`

The integration now also exposes a broader source-backed decoder profile set for the exact models and families that were recovered directly from `ProductPackageDetail`, including `IVEM6048_V1`, `IVEM_V1`, `IVEM4024_V1`, `IVBM8048`, `IVBM10048`, `6K`, `15K`, `25K`, `20K`, `50K Base`, `50K V2`, `IVPM`, `IVGM`, `IVAM`, `IVCM`, `IVDM`, and the known ToFrequency variants.

This is still intentionally narrower than the app's entire product matrix. Ambiguous or decompiler-damaged subtype constants are left out instead of being guessed.

## Persistent Energy Path

The current source-backed direction for persistent energy is:

- keep native inverter counters only where the row semantics are directly supported enough to be exported as stable entities today
- continue using native PV yield and load-consumption counters as the only stable onboard energy families
- derive persistent grid import/export, battery charge/discharge, generator, and smart-load energy from the source-backed real-time power sensors until a direct raw counter mapping is proven
- keep inferred `Energy[][]` rows available in diagnostics, but do not promote them to stable energy entities before the row semantics are recovered from source

Current integration implementation:

- persistent derived energy totals are accumulated locally from the source-backed power sensors using trapezoidal integration between coordinator samples
- those totals are persisted in Home Assistant storage and restored on startup
- oversized sample gaps are discarded so reconnects or temporary outages do not backfill energy across unobserved time spans
- derived totals stay explicitly separate from the native `Energy[][]` counters in naming and documentation

## BMaxMin Interpretation

`BMaxMin[0]` carries the max and min cell voltages.

`BMaxMin[1]` is treated as the matching cell indices, not temperatures. This is supported by the naming used in `RealtimeBattInfoJsonVO`:

- `maxVoltage2bms`
- `maxVoltageNum2bms`
- `minVoltage2bms`
- `minVoltageNum2bms`

The `Num` suffix aligns with cell-number semantics, not temperature semantics.

## Energy Matrix Status

The integration now exposes only the stable part of the inverter `Energy[][]` matrix as sensor families.

Current best read of the inner column order:

- column 0: observed placeholder or reserved slot
- column 1: likely month
- column 2: strongest today / daily candidate
- column 3: likely year
- column 4: likely total

Why column 2 is the strongest daily candidate:

- flattened per-device DTOs consistently order fields as month, today, year
- battery rows and grid/feed rows follow that same DTO naming pattern
- in the captured sample, column 2 is the only bucket that differs in the way a daily counter would differ while month, year, and total can legitimately coincide

Currently treated as stable:

- row 0: PV yield
- row 1: load consumption

Currently treated as inferred only:

- row 2: candidate grid feed/export row
- row 4: candidate battery charge row
- row 5: candidate battery discharge row

Known limits:

- No exact consumer of `TimeDataConnEntity.Energy` has been recovered from the decompiled tree beyond the field and getter.
- `EnergyDataRootEntity` contains both `feedKwh` and `acInputKwh`, so the current source tree does not uniquely prove which grid-side row is export versus import/input.
- `DataEnergyRootEntity` and `DeviceEnergyRootEntity` confirm that charge and discharge families exist, but they do not prove the raw row indexes for those families.
- The inner column order is still inferred from flattened DTO field order plus sample-value shape, not from a recovered `Energy[row][column]` consumer.
- Row 3 is intentionally not exported as a stable sensor family because the current codebase does not prove whether it is grid import, AC input, or another grid-side aggregate.
- Rows 8 and 9 are still observational only.
- Rows 2, 4, and 5 remain visible in `energy_decoder_status.inferred_rows`, but they are not exported as stable energy entities.

Until a direct mapper is recovered, the raw matrix remains useful as a diagnostic source and should stay documented as partially inferred. The raw diagnostic entity also exposes an `energy_decoder_status` attribute that explains which rows are stable and which remain intentionally unverified.