from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


PERSISTENT_ENERGY_SOURCE_KEYS: tuple[tuple[str, str], ...] = (
    ("persistent_grid_import_energy", "grid_import_power"),
    ("persistent_grid_export_energy", "grid_export_power"),
    ("persistent_battery_charge_energy", "battery_charge_power"),
    ("persistent_battery_discharge_energy", "battery_discharge_power"),
    ("persistent_generator_energy", "generator_power"),
    ("persistent_smart_load_energy", "smart_load_power"),
)


@dataclass(slots=True)
class PersistentEnergyAccumulator:
    max_gap_seconds: float
    totals_kwh: dict[str, float] = field(
        default_factory=lambda: {
            energy_key: 0.0 for energy_key, _ in PERSISTENT_ENERGY_SOURCE_KEYS
        }
    )
    _last_powers_w: dict[str, float | None] = field(
        default_factory=lambda: {
            energy_key: None for energy_key, _ in PERSISTENT_ENERGY_SOURCE_KEYS
        }
    )
    _last_sample_monotonic: float | None = None

    def restore(self, payload: Mapping[str, Any] | None) -> None:
        if not isinstance(payload, Mapping):
            return

        totals = payload.get("totals_kwh", payload)
        if not isinstance(totals, Mapping):
            return

        for energy_key, _ in PERSISTENT_ENERGY_SOURCE_KEYS:
            value = _non_negative_number(totals.get(energy_key))
            if value is not None:
                self.totals_kwh[energy_key] = value

        self._last_sample_monotonic = None
        self._last_powers_w = {
            energy_key: None for energy_key, _ in PERSISTENT_ENERGY_SOURCE_KEYS
        }

    def snapshot(self) -> dict[str, dict[str, float]]:
        return {
            "totals_kwh": {
                energy_key: round(total_kwh, 6)
                for energy_key, total_kwh in self.totals_kwh.items()
            }
        }

    def apply_sample(
        self,
        power_metrics: Mapping[str, Any],
        *,
        sampled_at_monotonic: float,
    ) -> dict[str, float]:
        current_powers_w = {
            energy_key: _non_negative_number(power_metrics.get(power_key))
            for energy_key, power_key in PERSISTENT_ENERGY_SOURCE_KEYS
        }

        if self._last_sample_monotonic is not None:
            delta_seconds = max(sampled_at_monotonic - self._last_sample_monotonic, 0.0)
            if 0.0 < delta_seconds <= self.max_gap_seconds:
                delta_hours = delta_seconds / 3600.0
                for energy_key, current_power_w in current_powers_w.items():
                    previous_power_w = self._last_powers_w[energy_key]
                    if current_power_w is None or previous_power_w is None:
                        continue

                    average_power_w = (previous_power_w + current_power_w) / 2.0
                    self.totals_kwh[energy_key] += (average_power_w * delta_hours) / 1000.0

        self._last_sample_monotonic = sampled_at_monotonic
        self._last_powers_w = current_powers_w
        return self.as_sensor_values()

    def as_sensor_values(self) -> dict[str, float]:
        return {
            energy_key: round(total_kwh, 3)
            for energy_key, total_kwh in self.totals_kwh.items()
        }


def _non_negative_number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return max(float(value), 0.0)
    return None