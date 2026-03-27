from __future__ import annotations

from typing import Any, Mapping


def sensor_key_is_supported(key: str, data: Mapping[str, Any]) -> bool:
    if key == "raw_json_payload":
        return bool(data.get("_raw_payloads"))
    return data.get(key) is not None


def binary_sensor_key_is_supported(key: str, data: Mapping[str, Any]) -> bool:
    support_values: dict[str, Any] = {
        "fault_active": data.get("inverter_fault_code"),
        "warning_active": data.get("inverter_warning_code"),
        "grid_connected": data.get("grid_voltage"),
        "battery_present": data.get("battery_voltage"),
        "bms_active": data.get("bms_is_active"),
        "bms_charging": data.get("bms_is_charging"),
    }
    return support_values.get(key) is not None