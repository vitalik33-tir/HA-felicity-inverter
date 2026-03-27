# Architecture

This integration is being refactored toward a pragmatic Home Assistant-friendly structure:

- Transport and raw JSON parsing stay in `custom_components/felicity_inverter/api.py`.
- Home Assistant setup and entity platform files stay thin and focused on coordinator wiring plus entity exposure.
- Reverse-engineered decoding logic lives in `custom_components/felicity_inverter/decoder/`.

## Data Flow

1. `api.py` polls the local TCP commands and splits concatenated JSON objects.
2. `decoder/selection.py` chooses the primary inverter packet and merges related BMS packets.
3. `decoder/profiles.py` resolves the current Type/SubType profile.
4. `decoder/power.py`, `decoder/bms.py`, and `decoder/energy.py` convert raw arrays into normalized values.
5. `decoder/normalize.py` assembles the stateless normalized telemetry dictionary.
6. `persistent_energy.py` accumulates derived total-energy sensors from the source-backed power metrics and persists them across restarts.
7. `sensor.py` and `binary_sensor.py` expose those normalized values as entities.

## Why This Layout

The old `telemetry.py` concentrated almost all decode logic in one file. That made it hard to audit which values were proven from decompiled source and which were still inferred. The decoder package makes that split explicit and keeps platform modules closer to standard Home Assistant patterns.

## Persistent Energy Direction

- Native device counters should be used where their semantics are source-backed.
- Derived persistent energy should be based on decoded power sensors, not directly on voltage and current, because AC energy semantics depend on phase and power-factor behavior.
- Native counters and derived persistent totals should stay clearly separated in naming and documentation.