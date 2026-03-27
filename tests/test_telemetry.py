from __future__ import annotations

import importlib
from pathlib import Path
import sys
import types
from typing import TYPE_CHECKING, Any
import unittest

if TYPE_CHECKING:
    from custom_components.felicity_inverter.api import ParsedResponse, RawPollData


def _load_telemetry_symbols() -> tuple[Any, Any, Any]:
    root = Path(__file__).resolve().parents[1]
    package_root = root / "custom_components"
    integration_root = package_root / "felicity_inverter"

    if "custom_components" not in sys.modules:
        custom_components_pkg = types.ModuleType("custom_components")
        custom_components_pkg.__path__ = [str(package_root)]
        sys.modules["custom_components"] = custom_components_pkg

    if "custom_components.felicity_inverter" not in sys.modules:
        integration_pkg = types.ModuleType("custom_components.felicity_inverter")
        integration_pkg.__path__ = [str(integration_root)]
        sys.modules["custom_components.felicity_inverter"] = integration_pkg

    api_module = importlib.import_module("custom_components.felicity_inverter.api")
    telemetry_module = importlib.import_module("custom_components.felicity_inverter.telemetry")
    return api_module.ParsedResponse, api_module.RawPollData, telemetry_module.normalize_telemetry


ParsedResponse, RawPollData, normalize_telemetry = _load_telemetry_symbols()


def _sample_poll_data() -> Any:
    real_objects = [
        {
            "CommVer": 1,
            "wifiSN": "WIFI-PRIMARY-001",
            "date": "20260310084150",
            "DevSN": "INV-PRIMARY-001",
            "Type": 80,
            "SubType": 1035,
            "workM": 3,
            "bCStat": 1,
            "pFlow": 62689,
            "warn": 0,
            "fault": 0,
            "lPerc": 30,
            "busVp": 4315,
            "BatTem": 15,
            "ACin": [[2224, None, None], [0, None, None], [4941, None, None], [0, 0], [0, None, None]],
            "ACout": [[2304, None, None], [9, None, None], [4941, None, None], [180, 207, 0], [180, None, None]],
            "PV": [[1823, 0, 0], [64, 0, 0], [1176, 0, 0], [0]],
            "Temp": [[380, 300, 340]],
            "Batt": [[55970], [140], [783, 0]],
            "Batsoc": [[9700, 0, 0]],
            "Energy": [
                [0, 1536, 1536, 1536, 1536],
                [0, 2485, 863, 2485, 2485],
                [0, 120, 240, 360, 480],
                [0, 80, 160, 240, 320],
                [0, 50, 100, 150, 200],
                [0, 40, 80, 120, 160],
            ],
            "GEN": [[0, None, None], [0, None, None], [0, None, None], [0, 0], [0, None, None]],
            "SmartL": [[0, None, None], [0, None, None], [0, None, None], [0, 0], [0, None, None]],
        },
        {
            "CommVer": 1,
            "wifiSN": "WIFI-PRIMARY-001",
            "version": "2.13",
            "DevSN": "BMS-PRIMARY-001",
            "InvSN": "INV-PRIMARY-001",
            "date": "20260310084150",
            "Type": 112,
            "Templist": [[190, 180], [1, 0], [None], [None]],
            "BattList": [[55870, None], [150, None]],
            "BatsocList": [[9700, 1000, 100000]],
            "BMaxMin": [[3520, 3490], [0, 3]],
            "BMSpara": [[1, 2]],
            "BLVolCu": [[576, 480], [150, 1000]],
            "Bstate": 9152,
            "BatcelList": [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]],
            "BtemList": [[0, 0, 0, 0, 0, 0, 0, 0]],
        },
    ]
    basic_objects = [
        {
            "CommVer": 1,
            "version": "2.13",
            "wifiSN": "WIFI-PRIMARY-001",
            "DevSN": "INV-PRIMARY-001",
            "Type": 80,
            "SubType": 1035,
            "DSwVer": 110,
            "DHwVer": 1000,
        },
        {
            "CommVer": 1,
            "wifiSN": "WIFI-PRIMARY-001",
            "version": "2.13",
            "DevSN": "BMS-PRIMARY-001",
            "Type": 112,
            "DSwVer": 65535,
            "DHwVer": 0,
            "InvSN": "INV-PRIMARY-001",
        },
    ]
    settings_objects = [
        {"CommVer": 1, "DevSN": "INV-PRIMARY-001", "ttlPack": 2, "index": 1, "Type": 80, "buzEn": 1},
        {"CommVer": 1, "DevSN": "INV-PRIMARY-001", "ttlPack": 2, "index": 2, "Type": 80, "FltClr": 0},
    ]

    return RawPollData(
        responses={
            "real": ParsedResponse(command="real", raw="real", objects=real_objects),
            "basic": ParsedResponse(command="basic", raw="basic", objects=basic_objects),
            "set": ParsedResponse(command="set", raw="set", objects=settings_objects),
        }
    )


class TelemetryNormalizationTests(unittest.TestCase):
    def test_normalize_telemetry_keeps_inverter_identity(self) -> None:
        data = normalize_telemetry(_sample_poll_data())

        self.assertEqual(data["device_serial"], "INV-PRIMARY-001")
        self.assertEqual(data["wifi_serial"], "WIFI-PRIMARY-001")
        self.assertEqual(data["firmware_version"], "2.13")
        self.assertEqual(data["device_software_version"], "110")
        self.assertEqual(data["device_hardware_version"], "1000")
        self.assertEqual(data["bms_firmware_version"], "2.13")
        self.assertEqual(data["bms_device_serial"], "BMS-PRIMARY-001")
        self.assertEqual(data["bms_inverter_serial"], "INV-PRIMARY-001")
        self.assertEqual(data["_raw_bms"]["DevSN"], "BMS-PRIMARY-001")

    def test_normalize_telemetry_extracts_sample_metrics(self) -> None:
        data = normalize_telemetry(_sample_poll_data())

        self.assertEqual(data["battery_voltage"], 55.87)
        self.assertEqual(data["battery_current"], 15.0)
        self.assertEqual(data["battery_power"], 838)
        self.assertEqual(data["battery_charge_power"], 838)
        self.assertEqual(data["battery_discharge_power"], 0)
        self.assertEqual(data["battery_soc"], 97.0)
        self.assertEqual(data["battery_state_of_health"], 100.0)
        self.assertEqual(data["battery_capacity"], 100.0)
        self.assertEqual(data["battery_charge_status"], "Charging")
        self.assertEqual(data["battery_charge_stage"], "Bulk")
        self.assertEqual(data["battery_charge_status_raw"], 1)
        self.assertEqual(data["pv_voltage"], 182.3)
        self.assertEqual(data["pv_current"], 6.4)
        self.assertEqual(data["pv_power"], 1176)
        self.assertEqual(data["pv_total_power"], 1176)
        self.assertEqual(data["pv1_voltage"], 182.3)
        self.assertEqual(data["pv1_current"], 6.4)
        self.assertEqual(data["pv1_power"], 1176)
        self.assertEqual(data["bus_voltage"], 431.5)
        self.assertEqual(data["inverter_mode"], "Battery")
        self.assertEqual(data["inverter_mode_raw"], 3)
        self.assertEqual(data["decoder_profile"], "ivem6048_v1")
        self.assertEqual(data["decoder_profile_label"], "IVEM6048_V1")
        self.assertEqual(data["inverter_temperature"], 38.0)
        self.assertEqual(data["transformer_temperature"], 38.0)
        self.assertEqual(data["heatsink_temperature"], 30.0)
        self.assertEqual(data["ambient_temperature"], 34.0)
        self.assertEqual(data["battery_temperature"], 15.0)
        self.assertEqual(data["grid_frequency"], 49.41)
        self.assertEqual(data["output_frequency"], 49.41)
        self.assertEqual(data["load_percent"], 3.0)
        self.assertEqual(data["load_power"], 180)
        self.assertEqual(data["load_total_power"], 180)
        self.assertEqual(data["load_apparent_power"], 207)
        self.assertEqual(data["power_flow_status_raw"], 62689)
        self.assertEqual(data["_power_methods"]["pv_total_power"], "sum(PV[2])")
        self.assertEqual(data["_power_methods"]["load_power"], "ACout[3][0]")
        self.assertEqual(data["_power_methods"]["grid_power"], "IVEM6048_V1/IVEM_V1 -> ACin[4][1]")
        self.assertEqual(
            data["_power_methods"]["battery_power"],
            "SocDataRootEntity.batteryPower() -> (BattList[0][0] / 1000) * (BattList[1][0] / 10)",
        )
        self.assertEqual(data["pv_yield_energy_total"], 1.536)
        self.assertEqual(data["pv_yield_energy_daily"], 1.536)
        self.assertEqual(data["load_consumption_energy_total"], 2.485)
        self.assertEqual(data["load_consumption_energy_daily"], 0.863)
        self.assertEqual(data["load_consumption_energy_monthly"], 2.485)
        self.assertNotIn("grid_export_energy_total", data)
        self.assertNotIn("battery_charge_energy_total", data)
        self.assertNotIn("battery_discharge_energy_total", data)
        self.assertNotIn("grid_import_energy_total", data)
        self.assertNotIn("pv_to_load_power", data)
        self.assertNotIn("pv_to_battery_power", data)
        self.assertNotIn("pv_to_grid_power", data)
        self.assertNotIn("battery_to_load_power", data)
        self.assertNotIn("grid_to_load_power", data)
        self.assertNotIn("self_consumption_power", data)
        self.assertNotIn("self_consumption_percent", data)
        self.assertNotIn("battery_roundtrip_efficiency", data)
        self.assertNotIn("wifi_status", data)
        self.assertNotIn("bms_communication_status", data)
        self.assertNotIn("bms_registration_status", data)
        self.assertNotIn("bms_global_status", data)
        self.assertNotIn("charge_source_priority", data)
        self.assertNotIn("smart_port_status", data)
        self.assertNotIn("system_power_status", data)
        self.assertEqual(data["bms_pack_voltage"], 55.87)
        self.assertEqual(data["bms_pack_current"], 15.0)
        self.assertEqual(data["bms_pack_soc"], 97.0)
        self.assertEqual(data["bms_total_capacity"], 100.0)
        self.assertEqual(data["bms_max_cell_voltage"], 3.52)
        self.assertEqual(data["bms_min_cell_voltage"], 3.49)
        self.assertEqual(data["bms_max_cell_index"], 0)
        self.assertEqual(data["bms_min_cell_index"], 3)
        self.assertTrue(data["bms_is_charging"])
        self.assertTrue(data["bms_is_active"])
        self.assertEqual(
            data["_energy_decoder_status"]["inferred_rows"]["grid_export_energy"]["scaled_values_kwh"]["total"],
            0.48,
        )
        self.assertEqual(
            data["_energy_decoder_status"]["inferred_rows"]["battery_charge_energy"]["scaled_values_kwh"]["total"],
            0.2,
        )
        self.assertEqual(
            data["_energy_decoder_status"]["inferred_rows"]["battery_discharge_energy"]["scaled_values_kwh"]["total"],
            0.16,
        )
        self.assertEqual(
            data["_energy_decoder_status"]["unverified_rows"]["row_3"]["scaled_values_kwh"]["total"],
            0.32,
        )
        self.assertNotIn("bms_max_cell_temperature", data)
        self.assertNotIn("inverter_throughput_energy", data)

    def test_normalize_telemetry_supports_power_first_ac_layout(self) -> None:
        poll_data = RawPollData(
            responses={
                "real": ParsedResponse(
                    command="real",
                    raw="real",
                    objects=[
                        {
                            "DevSN": "INV-1",
                            "Type": 80,
                            "SubType": 1035,
                            "workM": 1,
                            "ACin": [[2300], [100], [2500], [5000, 2500], [0]],
                            "ACout": [[2300], [100], [1500], [5000, 1500], [0]],
                            "PV": [[1000, 0, 0], [30, 0, 0], [300, 0, 0], [0]],
                            "Batt": [[52000], [50], [-200, 0]],
                            "Batsoc": [[8000, 0, 0]],
                        }
                    ],
                ),
                "basic": ParsedResponse(
                    command="basic",
                    raw="basic",
                    objects=[
                        {
                            "DevSN": "INV-1",
                            "Type": 80,
                            "version": "2.20",
                            "DSwVer": 200,
                            "DHwVer": 1000,
                        }
                    ],
                ),
                "set": ParsedResponse(command="set", raw="set", objects=[]),
            }
        )

        data = normalize_telemetry(poll_data)

        self.assertEqual(data["inverter_mode"], "Standby")
        self.assertEqual(data["grid_import_power"], 0)
        self.assertEqual(data["grid_power"], 0)
        self.assertEqual(data["grid_frequency"], 50.0)
        self.assertEqual(data["load_power"], 5000)
        self.assertEqual(data["load_total_power"], 5000)
        self.assertEqual(data["output_frequency"], 50.0)
        self.assertEqual(data["pv_power"], 300)
        self.assertEqual(data["pv_total_power"], 300)
        self.assertEqual(data["battery_charge_power"], 0)
        self.assertEqual(data["battery_discharge_power"], 200)
        self.assertEqual(data["_power_methods"]["grid_power"], "IVEM6048_V1/IVEM_V1 -> ACin[4][1]")
        self.assertEqual(data["_power_methods"]["battery_power"], "Batt[2][0]")

    def test_normalize_telemetry_ignores_battery_discharge_in_work_mode_5_grid_fallback(self) -> None:
        poll_data = RawPollData(
            responses={
                "real": ParsedResponse(
                    command="real",
                    raw="real",
                    objects=[
                        {
                            "DevSN": "INV-BYPASS-1",
                            "Type": 80,
                            "SubType": 1035,
                            "workM": 5,
                            "ACin": [[2299, None, None], [0, None, None], [4831, None, None], [0, 0], [0, None, None]],
                            "ACout": [[2299, None, None], [19, None, None], [4831, None, None], [414, 436, 0], [414, None, None]],
                            "PV": [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0]],
                            "Batt": [[52500], [-20], [-110, 0]],
                            "Batsoc": [[4200, 0, 0]],
                        }
                    ],
                ),
                "basic": ParsedResponse(
                    command="basic",
                    raw="basic",
                    objects=[
                        {
                            "DevSN": "INV-BYPASS-1",
                            "Type": 80,
                            "SubType": 1035,
                            "version": "2.20",
                        }
                    ],
                ),
                "set": ParsedResponse(command="set", raw="set", objects=[]),
            }
        )

        data = normalize_telemetry(poll_data)

        self.assertEqual(data["inverter_mode"], "Grid")
        self.assertEqual(data["battery_power"], -110)
        self.assertEqual(data["battery_discharge_power"], 110)
        self.assertEqual(data["pv_total_power"], 0)
        self.assertEqual(data["load_power"], 414)
        self.assertEqual(data["grid_power"], 414)
        self.assertEqual(data["grid_import_power"], 414)
        self.assertEqual(data["grid_export_power"], 0)
        self.assertEqual(data["_power_methods"]["grid_power"], "IVEM workM=5 fallback -> load + max(battery, 0) - pv")

    def test_normalize_telemetry_maps_unknown_inverter_mode_to_raw_string(self) -> None:
        poll_data = RawPollData(
            responses={
                "real": ParsedResponse(
                    command="real",
                    raw="real",
                    objects=[
                        {
                            "DevSN": "INV-UNKNOWN-MODE",
                            "Type": 80,
                            "SubType": 1035,
                            "workM": 9,
                            "Batt": [[52000], [0], [0, 0]],
                            "Batsoc": [[8000, 0, 0]],
                        }
                    ],
                ),
                "basic": ParsedResponse(
                    command="basic",
                    raw="basic",
                    objects=[
                        {
                            "DevSN": "INV-UNKNOWN-MODE",
                            "Type": 80,
                            "SubType": 1035,
                            "version": "2.20",
                        }
                    ],
                ),
                "set": ParsedResponse(command="set", raw="set", objects=[]),
            }
        )

        data = normalize_telemetry(poll_data)

        self.assertEqual(data["inverter_mode"], "9")
        self.assertEqual(data["inverter_mode_raw"], 9)

    def test_normalize_telemetry_supports_per_string_pv_layout(self) -> None:
        poll_data = RawPollData(
            responses={
                "real": ParsedResponse(
                    command="real",
                    raw="real",
                    objects=[
                        {
                            "DevSN": "INV-3",
                            "Type": 80,
                            "SubType": 1035,
                            "PV": [[1200, 50, 600], [1100, 40, 440], [0, 0, 0], [1040]],
                            "Batt": [[52000], [0], [0, 0]],
                            "Batsoc": [[8000, 0, 0]],
                        }
                    ],
                ),
                "basic": ParsedResponse(
                    command="basic",
                    raw="basic",
                    objects=[{"DevSN": "INV-3", "Type": 80, "version": "2.20"}],
                ),
                "set": ParsedResponse(command="set", raw="set", objects=[]),
            }
        )

        data = normalize_telemetry(poll_data)

        self.assertEqual(data["pv1_voltage"], 120.0)
        self.assertEqual(data["pv1_current"], 5.0)
        self.assertEqual(data["pv1_power"], 600)
        self.assertEqual(data["pv2_voltage"], 110.0)
        self.assertEqual(data["pv2_current"], 4.0)
        self.assertEqual(data["pv2_power"], 440)
        self.assertEqual(data["pv3_voltage"], 0.0)
        self.assertEqual(data["pv3_current"], 0.0)
        self.assertEqual(data["pv3_power"], 0)
        self.assertEqual(data["pv_power"], 0)
        self.assertEqual(data["pv_total_power"], 0)
        self.assertEqual(data["_ac_layouts"]["pv"], "legacy")
        self.assertEqual(data["_power_methods"]["pv_total_power"], "sum(PV[2])")

    def test_normalize_telemetry_resolves_source_backed_profiles(self) -> None:
        cases = (
            ((80, 17422), ("ivbm_8048", "IVBM8048")),
            ((337, 1056), ("6k", "6K")),
            ((82, None), ("50k_base", "50K Base")),
            ((16, 1042), ("to_frequency_1042", "ToFrequency1042")),
            ((80, 21514), ("ivem_can_feed", "IVEM Feed Variant")),
        )

        for (type_id, subtype_id), (expected_key, expected_label) in cases:
            with self.subTest(type_id=type_id, subtype_id=subtype_id):
                real_object = {
                    "DevSN": f"INV-{type_id}-{subtype_id}",
                    "Type": type_id,
                    "Batt": [[52000], [0], [0, 0]],
                    "Batsoc": [[8000, 0, 0]],
                }
                if subtype_id is not None:
                    real_object["SubType"] = subtype_id

                poll_data = RawPollData(
                    responses={
                        "real": ParsedResponse(command="real", raw="real", objects=[real_object]),
                        "basic": ParsedResponse(
                            command="basic",
                            raw="basic",
                            objects=[
                                {
                                    "DevSN": f"INV-{type_id}-{subtype_id}",
                                    "Type": type_id,
                                    **({"SubType": subtype_id} if subtype_id is not None else {}),
                                }
                            ],
                        ),
                        "set": ParsedResponse(command="set", raw="set", objects=[]),
                    }
                )

                data = normalize_telemetry(poll_data)

                self.assertEqual(data["decoder_profile"], expected_key)
                self.assertEqual(data["decoder_profile_label"], expected_label)
