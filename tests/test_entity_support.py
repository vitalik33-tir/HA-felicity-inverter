from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


def _load_support_symbols() -> tuple[object, object]:
    root = Path(__file__).resolve().parents[1]
    module_path = root / "custom_components" / "felicity_inverter" / "entity_support.py"
    spec = importlib.util.spec_from_file_location("felicity_entity_support", module_path)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load entity_support module for tests")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.sensor_key_is_supported, module.binary_sensor_key_is_supported


sensor_key_is_supported, binary_sensor_key_is_supported = _load_support_symbols()


class EntitySupportTests(unittest.TestCase):
    def test_sensor_support_requires_value(self) -> None:
        data = {
            "battery_soc": 97.0,
            "battery_charge_stage": None,
            "_raw_payloads": {"real": "payload"},
        }

        self.assertTrue(sensor_key_is_supported("battery_soc", data))
        self.assertFalse(sensor_key_is_supported("battery_charge_stage", data))
        self.assertTrue(sensor_key_is_supported("raw_json_payload", data))

    def test_sensor_support_hides_raw_payload_without_payloads(self) -> None:
        self.assertFalse(sensor_key_is_supported("raw_json_payload", {}))

    def test_binary_sensor_support_follows_backing_metrics(self) -> None:
        data = {
            "inverter_fault_code": 0,
            "inverter_warning_code": None,
            "grid_voltage": 230.0,
            "battery_voltage": None,
            "bms_is_active": True,
            "bms_is_charging": None,
        }

        self.assertTrue(binary_sensor_key_is_supported("fault_active", data))
        self.assertFalse(binary_sensor_key_is_supported("warning_active", data))
        self.assertTrue(binary_sensor_key_is_supported("grid_connected", data))
        self.assertFalse(binary_sensor_key_is_supported("battery_present", data))
        self.assertTrue(binary_sensor_key_is_supported("bms_active", data))
        self.assertFalse(binary_sensor_key_is_supported("bms_charging", data))