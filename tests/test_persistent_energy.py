from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


def _load_persistent_energy_symbols() -> tuple[object, object]:
    root = Path(__file__).resolve().parents[1]
    module_path = root / "custom_components" / "felicity_inverter" / "persistent_energy.py"
    spec = importlib.util.spec_from_file_location("felicity_persistent_energy", module_path)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load persistent_energy module for tests")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.PersistentEnergyAccumulator, module.PERSISTENT_ENERGY_SOURCE_KEYS


PersistentEnergyAccumulator, PERSISTENT_ENERGY_SOURCE_KEYS = _load_persistent_energy_symbols()


class PersistentEnergyAccumulatorTests(unittest.TestCase):
    def test_accumulator_integrates_trapezoidally_after_first_sample(self) -> None:
        accumulator = PersistentEnergyAccumulator(max_gap_seconds=7200)

        first = accumulator.apply_sample(
            {
                "grid_import_power": 1000,
                "battery_charge_power": 500,
            },
            sampled_at_monotonic=0,
        )
        second = accumulator.apply_sample(
            {
                "grid_import_power": 1000,
                "battery_charge_power": 500,
            },
            sampled_at_monotonic=3600,
        )

        self.assertEqual(first["persistent_grid_import_energy"], 0.0)
        self.assertEqual(first["persistent_battery_charge_energy"], 0.0)
        self.assertEqual(second["persistent_grid_import_energy"], 1.0)
        self.assertEqual(second["persistent_battery_charge_energy"], 0.5)

    def test_accumulator_skips_large_gaps(self) -> None:
        accumulator = PersistentEnergyAccumulator(max_gap_seconds=30)

        accumulator.apply_sample({"grid_import_power": 1000}, sampled_at_monotonic=0)
        after_gap = accumulator.apply_sample({"grid_import_power": 1000}, sampled_at_monotonic=120)
        after_resume = accumulator.apply_sample({"grid_import_power": 1000}, sampled_at_monotonic=130)

        self.assertEqual(after_gap["persistent_grid_import_energy"], 0.0)
        self.assertEqual(after_resume["persistent_grid_import_energy"], 0.003)

    def test_accumulator_does_not_bridge_unavailable_samples(self) -> None:
        accumulator = PersistentEnergyAccumulator(max_gap_seconds=60)

        accumulator.apply_sample({"grid_export_power": 600}, sampled_at_monotonic=0)
        missing = accumulator.apply_sample({"grid_export_power": None}, sampled_at_monotonic=10)
        resumed = accumulator.apply_sample({"grid_export_power": 600}, sampled_at_monotonic=20)
        integrated = accumulator.apply_sample({"grid_export_power": 600}, sampled_at_monotonic=30)

        self.assertEqual(missing["persistent_grid_export_energy"], 0.0)
        self.assertEqual(resumed["persistent_grid_export_energy"], 0.0)
        self.assertEqual(integrated["persistent_grid_export_energy"], 0.002)

    def test_accumulator_restores_snapshot(self) -> None:
        accumulator = PersistentEnergyAccumulator(max_gap_seconds=60)
        accumulator.restore(
            {
                "totals_kwh": {
                    "persistent_grid_import_energy": 12.345678,
                    "persistent_battery_discharge_energy": 4.5,
                }
            }
        )

        restored = accumulator.as_sensor_values()
        snapshot = accumulator.snapshot()

        self.assertEqual(restored["persistent_grid_import_energy"], 12.346)
        self.assertEqual(restored["persistent_battery_discharge_energy"], 4.5)
        self.assertEqual(snapshot["totals_kwh"]["persistent_grid_import_energy"], 12.345678)

    def test_accumulator_exposes_all_expected_energy_keys(self) -> None:
        accumulator = PersistentEnergyAccumulator(max_gap_seconds=60)

        self.assertEqual(
            set(accumulator.as_sensor_values()),
            {energy_key for energy_key, _ in PERSISTENT_ENERGY_SOURCE_KEYS},
        )