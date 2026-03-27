from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Any

from .constants import BATTERY_CHARGE_STAGE_LABELS
from .helpers import (
    bit_is_set,
    integer,
    map_enum,
    nested,
    normalize_temperature,
    scaled_number,
)


def battery_charge_status(inverter: dict[str, Any], bms: dict[str, Any]) -> str | None:
    flags = decode_bms_state_flags(bms)
    is_charging = flags["bms_is_charging"]
    if is_charging is True:
        return "Charging"
    if is_charging is False:
        return "Idle or Discharging"
    return battery_charge_stage(inverter)


def battery_charge_stage(inverter: dict[str, Any]) -> str | None:
    return map_enum(inverter.get("bCStat"), BATTERY_CHARGE_STAGE_LABELS)


def decode_bms_state_flags(bms: dict[str, Any]) -> dict[str, Any]:
    raw_state = integer(bms.get("Bstate"))
    if raw_state is None:
        return {
            "bms_state": None,
            "bms_is_charging": None,
            "bms_is_active": None,
        }

    is_charging = bit_is_set(raw_state, 13)
    is_active = bit_is_set(raw_state, 12) or is_charging
    return {
        "bms_state": raw_state,
        "bms_is_charging": is_charging,
        "bms_is_active": is_active,
    }


def battery_power_from_bms(bms: dict[str, Any]) -> float | None:
    """Mirror SocDataRootEntity.batteryPower() when BattList values are present."""
    voltage = _battery_voltage_decimal(bms)
    current = _battery_current_decimal(bms)
    if voltage is None or current is None:
        return None
    power = (voltage * current).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(power)


def extract_bms_metrics(bms: dict[str, Any]) -> dict[str, Any]:
    return {
        **decode_bms_state_flags(bms),
        "bms_fault_code": integer(bms.get("BBfault")),
        "bms_warning_code": integer(bms.get("BBwarn")),
        "bms_pack_voltage": scaled_number(nested(bms, "BattList", 0, 0), 0.001, 2),
        "bms_pack_current": scaled_number(nested(bms, "BattList", 1, 0), 0.1, 1),
        "bms_pack_soc": scaled_number(nested(bms, "BatsocList", 0, 0), 0.01, 1),
        "bms_pack_state_of_health": scaled_number(
            nested(bms, "BatsocList", 0, 1),
            0.1,
            1,
        ),
        "bms_total_capacity": scaled_number(nested(bms, "BatsocList", 0, 2), 0.001, 3),
        "bms_max_cell_voltage": scaled_number(nested(bms, "BMaxMin", 0, 0), 0.001, 3),
        "bms_min_cell_voltage": scaled_number(nested(bms, "BMaxMin", 0, 1), 0.001, 3),
        "bms_max_cell_index": integer(nested(bms, "BMaxMin", 1, 0)),
        "bms_min_cell_index": integer(nested(bms, "BMaxMin", 1, 1)),
        "bms_parallel_count": integer(nested(bms, "BMSpara", 0, 0)),
        "bms_hardware_config": integer(nested(bms, "BMSpara", 0, 1)),
        "bms_charge_voltage_limit": scaled_number(nested(bms, "BLVolCu", 0, 0), 0.1, 1),
        "bms_discharge_voltage_limit": scaled_number(
            nested(bms, "BLVolCu", 0, 1),
            0.1,
            1,
        ),
        "bms_charge_current_limit": scaled_number(nested(bms, "BLVolCu", 1, 0), 0.1, 1),
        "bms_discharge_current_limit": scaled_number(
            nested(bms, "BLVolCu", 1, 1),
            0.1,
            1,
        ),
        "bms_temperature_1": normalize_temperature(nested(bms, "Templist", 0, 0)),
        "bms_temperature_2": normalize_temperature(nested(bms, "Templist", 0, 1)),
    }


def _battery_voltage_decimal(bms: dict[str, Any]) -> Decimal | None:
    return _scaled_decimal(nested(bms, "BattList", 0, 0), divisor=1000)


def _battery_current_decimal(bms: dict[str, Any]) -> Decimal | None:
    return _scaled_decimal(nested(bms, "BattList", 1, 0), divisor=10)


def _scaled_decimal(value: Any, *, divisor: int) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None
    return (decimal_value / Decimal(divisor)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)