from __future__ import annotations

from typing import Any

from ..api import RawPollData, merge_json_objects
from .bms import (
    battery_charge_stage,
    battery_charge_status,
    battery_power_from_bms,
    extract_bms_metrics,
)
from .constants import INVERTER_OPERATING_MODE_LABELS
from .energy import energy_decoder_status, extract_energy_metrics
from .helpers import (
    coerce_string,
    first_number,
    integer,
    map_enum,
    nested,
    normalize_temperature,
    number,
    round_number,
    scaled_number,
)
from .power import (
    extract_ac_metrics,
    extract_pv_metrics,
    extract_source_backed_power_metrics,
)
from .profiles import resolve_model_profile
from .selection import collect_bms_objects, merge_inverter_objects, response_objects


def normalize_telemetry(
    raw_data: RawPollData,
    *,
    host: str | None = None,
    port: int | None = None,
) -> dict[str, Any]:
    real_objects = response_objects(raw_data, "real")
    basic_objects = response_objects(raw_data, "basic")
    settings_objects = response_objects(raw_data, "set")

    inverter_real = merge_inverter_objects(real_objects)
    inverter_serial = coerce_string(inverter_real.get("DevSN"))

    inverter_basic = merge_inverter_objects(basic_objects, inverter_serial=inverter_serial)
    if inverter_serial is None:
        inverter_serial = coerce_string(inverter_basic.get("DevSN"))
        inverter_real = merge_inverter_objects(real_objects, inverter_serial=inverter_serial)

    inverter_settings = merge_inverter_objects(
        settings_objects,
        inverter_serial=inverter_serial,
    )

    inverter: dict[str, Any] = {}
    inverter.update(inverter_settings)
    inverter.update(inverter_basic)
    inverter.update(inverter_real)

    bms_objects = (
        collect_bms_objects(real_objects, inverter_serial=inverter_serial)
        + collect_bms_objects(basic_objects, inverter_serial=inverter_serial)
    )
    bms = merge_json_objects(bms_objects)

    profile = resolve_model_profile(inverter)

    source_power = extract_source_backed_power_metrics(inverter)
    pv_metrics = extract_pv_metrics(inverter.get("PV"))
    grid_metrics = extract_ac_metrics(inverter.get("ACin"))
    load_metrics = extract_ac_metrics(inverter.get("ACout"))
    generator_metrics = extract_ac_metrics(inverter.get("GEN"))
    smart_load_metrics = extract_ac_metrics(inverter.get("SmartL"))
    energy_metrics = extract_energy_metrics(inverter.get("Energy"))
    energy_status = energy_decoder_status(inverter.get("Energy"))
    bms_metrics = extract_bms_metrics(bms)

    battery_voltage_raw = first_number(
        nested(bms, "BattList", 0, 0),
        nested(inverter, "Batt", 0, 0),
    )
    battery_current_raw = first_number(
        nested(bms, "BattList", 1, 0),
        nested(inverter, "Batt", 1, 0),
    )

    battery_voltage = scaled_number(battery_voltage_raw, 0.001, 2)
    battery_current = scaled_number(battery_current_raw, 0.1, 1)
    bms_battery_power = battery_power_from_bms(bms)
    if bms_battery_power is not None:
        battery_power = round_number(bms_battery_power, 0)
        battery_power_method = "SocDataRootEntity.batteryPower() -> (BattList[0][0] / 1000) * (BattList[1][0] / 10)"
    else:
        battery_power = source_power["battery_power"]
        battery_power_method = source_power["branches"]["battery_power"]

    battery_charge_power: float | int | None = None
    battery_discharge_power: float | int | None = None
    battery_charge_current: float | int | None = None
    battery_discharge_current: float | int | None = None
    if battery_power is not None:
        if battery_power > 0:
            battery_discharge_power = 0
            battery_charge_power = battery_power
            battery_discharge_current = 0
            battery_charge_current = abs(float(battery_current)) if battery_current is not None else 0
        elif battery_power < 0:
            battery_discharge_power = round_number(abs(float(battery_power)), 0)
            battery_charge_power = 0
            battery_discharge_current = abs(float(battery_current)) if battery_current is not None else 0
            battery_charge_current = 0
        else:
            battery_charge_power = 0
            battery_discharge_power = 0
            battery_charge_current = 0
            battery_discharge_current = 0

    battery_soc = scaled_number(
        first_number(
            nested(inverter, "Batsoc", 0, 0),
            nested(bms, "BatsocList", 0, 0),
        ),
        0.01,
        1,
    )

    inverter_soh_raw = number(nested(inverter, "Batsoc", 0, 1))
    if inverter_soh_raw is not None and inverter_soh_raw > 0:
        battery_state_of_health = round_number(inverter_soh_raw, 1)
    else:
        battery_state_of_health = scaled_number(nested(bms, "BatsocList", 0, 1), 0.1, 1)

    battery_capacity = scaled_number(nested(bms, "BatsocList", 0, 2), 0.001, 3)

    transformer_temperature = scaled_number(nested(inverter, "Temp", 0, 0), 0.1, 1)
    heatsink_temperature = scaled_number(nested(inverter, "Temp", 0, 1), 0.1, 1)
    ambient_temperature = scaled_number(nested(inverter, "Temp", 0, 2), 0.1, 1)
    battery_temperature = normalize_temperature(inverter.get("BatTem"))

    grid_power = source_power["grid_power"]
    grid_import_power = None if grid_power is None else round_number(max(float(grid_power), 0.0), 0)
    grid_export_power = None if grid_power is None else round_number(max(-float(grid_power), 0.0), 0)

    power_methods = dict(source_power["branches"])
    power_methods["battery_power"] = battery_power_method

    normalized: dict[str, Any] = {
        "communication_protocol_version": integer(inverter.get("CommVer") or inverter_basic.get("CommVer")),
        "device_serial": coerce_string(inverter.get("DevSN")) or inverter_serial,
        "wifi_serial": coerce_string(inverter.get("wifiSN") or inverter_basic.get("wifiSN")),
        "firmware_version": coerce_string(inverter.get("version") or inverter_basic.get("version")),
        "device_software_version": coerce_string(inverter.get("DSwVer") or inverter_basic.get("DSwVer")),
        "device_hardware_version": coerce_string(inverter.get("DHwVer") or inverter_basic.get("DHwVer")),
        "device_type": inverter.get("Type") or inverter_basic.get("Type"),
        "device_subtype": inverter.get("SubType") or inverter_basic.get("SubType"),
        "decoder_profile": profile.key,
        "decoder_profile_label": profile.label,
        "last_update": coerce_string(inverter.get("date")),
        "bms_firmware_version": coerce_string(bms.get("version")),
        "bms_device_serial": coerce_string(bms.get("DevSN")),
        "bms_inverter_serial": coerce_string(bms.get("InvSN")),
        "bms_modbus_address": integer(bms.get("ModAddr")),
        "bms_last_update": coerce_string(bms.get("date")),
        "load_percent": scaled_number(inverter.get("lPerc"), 0.1, 1),
        "bus_voltage": scaled_number(inverter.get("busVp"), 0.1, 1),
        "bus_negative_voltage": scaled_number(inverter.get("busVn"), 0.1, 1),
        "battery_soc": battery_soc,
        "battery_state_of_health": battery_state_of_health,
        "battery_capacity": battery_capacity,
        "battery_voltage": battery_voltage,
        "battery_current": battery_current,
        "battery_power": battery_power,
        "battery_charge_power": battery_charge_power,
        "battery_discharge_power": battery_discharge_power,
        "battery_charge_current": round_number(battery_charge_current, 1),
        "battery_discharge_current": round_number(battery_discharge_current, 1),
        "battery_temperature": battery_temperature,
        "battery_charge_status": battery_charge_status(inverter, bms),
        "battery_charge_stage": battery_charge_stage(inverter),
        "battery_charge_status_raw": integer(inverter.get("bCStat")),
        "pv_voltage": pv_metrics["voltage"],
        "pv_current": pv_metrics["current"],
        "pv_power": source_power["pv_total_power"],
        "pv_total_power": source_power["pv_total_power"],
        "pv1_voltage": pv_metrics["pv1_voltage"],
        "pv1_current": pv_metrics["pv1_current"],
        "pv1_power": pv_metrics["pv1_power"],
        "pv2_voltage": pv_metrics["pv2_voltage"],
        "pv2_current": pv_metrics["pv2_current"],
        "pv2_power": pv_metrics["pv2_power"],
        "pv3_voltage": pv_metrics["pv3_voltage"],
        "pv3_current": pv_metrics["pv3_current"],
        "pv3_power": pv_metrics["pv3_power"],
        "grid_voltage": grid_metrics["voltage"],
        "grid_current": grid_metrics["current"],
        "grid_frequency": grid_metrics["frequency"],
        "grid_power": grid_power,
        "grid_import_power": grid_import_power,
        "grid_export_power": grid_export_power,
        "grid_apparent_power": grid_metrics["apparent_power"],
        "grid_total_power": source_power["grid_total_power"],
        "load_voltage": load_metrics["voltage"],
        "load_current": load_metrics["current"],
        "output_frequency": load_metrics["frequency"],
        "load_power": source_power["load_power"],
        "load_apparent_power": load_metrics["apparent_power"],
        "load_total_power": source_power["load_total_power"],
        "generator_voltage": generator_metrics["voltage"],
        "generator_current": generator_metrics["current"],
        "generator_frequency": generator_metrics["frequency"],
        "generator_power": source_power["generator_power"],
        "generator_apparent_power": generator_metrics["apparent_power"],
        "generator_total_power": source_power["generator_total_power"],
        "smart_load_voltage": smart_load_metrics["voltage"],
        "smart_load_current": smart_load_metrics["current"],
        "smart_load_frequency": smart_load_metrics["frequency"],
        "smart_load_power": source_power["smart_load_power"],
        "smart_load_apparent_power": smart_load_metrics["apparent_power"],
        "smart_load_total_power": source_power["smart_load_total_power"],
        "transformer_temperature": transformer_temperature,
        "heatsink_temperature": heatsink_temperature,
        "ambient_temperature": ambient_temperature,
        "inverter_temperature": transformer_temperature,
        "inverter_mode": map_enum(inverter.get("workM"), INVERTER_OPERATING_MODE_LABELS),
        "inverter_mode_raw": integer(inverter.get("workM")),
        "inverter_warning_code": inverter.get("warn"),
        "inverter_fault_code": inverter.get("fault"),
        "power_flow_status_raw": integer(inverter.get("pFlow")),
        "power_flow_secondary_status_raw": integer(inverter.get("pFlowE1")),
        **energy_metrics,
        "bms_count": integer(inverter.get("bmsNum")),
        "wifi_status_raw": integer(inverter.get("setWifi")),
        "bms_communication_status_raw": integer(inverter.get("BMSFlE")),
        "bms_registration_status_raw": integer(inverter.get("BMSFlg")),
        "bms_global_status_raw": integer(inverter.get("BFlgAll")),
        "charge_source_priority_raw": integer(inverter.get("cSPri")),
        "max_ac_charge_current_limit": round_number(inverter.get("MACCurr"), 0),
        "smart_port_status_raw": integer(inverter.get("SmartS")),
        "system_power_status_raw": integer(inverter.get("SPStus")),
        **bms_metrics,
        "raw_json_payload": coerce_string(inverter.get("date")) or "available",
        "_raw_payloads": {
            key: response.raw
            for key, response in raw_data.responses.items()
            if response.raw is not None
        },
        "_raw_objects": {
            key: response.objects
            for key, response in raw_data.responses.items()
        },
        "_raw_inverter": inverter,
        "_raw_bms": bms,
        "_raw_settings": inverter_settings,
        "_raw_energy_counters": inverter.get("Energy"),
        "_energy_decoder_status": energy_status,
        "_power_methods": power_methods,
        "_ac_layouts": {
            "grid": grid_metrics["layout"],
            "load": load_metrics["layout"],
            "generator": generator_metrics["layout"],
            "smart_load": smart_load_metrics["layout"],
            "pv": pv_metrics["layout"],
        },
    }

    if host is not None:
        normalized["host"] = host
    if port is not None:
        normalized["port"] = port

    return normalized