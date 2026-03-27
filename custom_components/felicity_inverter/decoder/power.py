from __future__ import annotations

from typing import Any

from .helpers import (
    coerce_string,
    first_non_zero_number,
    integer,
    nested,
    number,
    round_number,
    scaled_number,
    sum_numbers,
)


def extract_pv_metrics(block: Any) -> dict[str, Any]:
    if pv_is_row_aggregated(block):
        voltage = scaled_number(nested(block, 0, 0), 0.1, 1)
        current = scaled_number(nested(block, 1, 0), 0.1, 1)
        power = round_number(nested(block, 2, 0), 0)
        total_power = round_number(
            first_non_zero_number(nested(block, 3, 0), nested(block, 2, 0)),
            0,
        )
        return {
            "layout": "row_aggregated",
            "voltage": voltage,
            "current": current,
            "power": power,
            "total_power": total_power if total_power is not None else power,
            "pv1_voltage": voltage,
            "pv1_current": current,
            "pv1_power": power,
            "pv2_voltage": None,
            "pv2_current": None,
            "pv2_power": None,
            "pv3_voltage": None,
            "pv3_current": None,
            "pv3_power": None,
        }

    pv1_voltage = scaled_number(nested(block, 0, 0), 0.1, 1)
    pv1_current = scaled_number(nested(block, 0, 1), 0.1, 1)
    pv1_power = round_number(nested(block, 0, 2), 0)

    pv2_voltage = scaled_number(nested(block, 1, 0), 0.1, 1)
    pv2_current = scaled_number(nested(block, 1, 1), 0.1, 1)
    pv2_power = round_number(nested(block, 1, 2), 0)

    pv3_voltage = scaled_number(nested(block, 2, 0), 0.1, 1)
    pv3_current = scaled_number(nested(block, 2, 1), 0.1, 1)
    pv3_power = round_number(nested(block, 2, 2), 0)

    total_power = round_number(nested(block, 3, 0), 0)

    if pv_is_aggregated(block):
        pv1_voltage = scaled_number(nested(block, 0, 0), 0.1, 1)
        pv1_current = scaled_number(nested(block, 1, 0), 0.1, 1)
        pv1_power = round_number(
            first_non_zero_number(nested(block, 2, 0), nested(block, 3, 0)),
            0,
        )
        total_power = round_number(
            first_non_zero_number(nested(block, 3, 0), nested(block, 2, 0)),
            0,
        )
        return {
            "layout": "aggregated",
            "voltage": pv1_voltage,
            "current": pv1_current,
            "power": pv1_power,
            "total_power": total_power if total_power is not None else pv1_power,
            "pv1_voltage": pv1_voltage,
            "pv1_current": pv1_current,
            "pv1_power": pv1_power,
            "pv2_voltage": None,
            "pv2_current": None,
            "pv2_power": None,
            "pv3_voltage": None,
            "pv3_current": None,
            "pv3_power": None,
        }

    total_current = sum_numbers(pv1_current, pv2_current, pv3_current)
    if total_power is None:
        total_power = round_number(sum_numbers(pv1_power, pv2_power, pv3_power), 0)

    return {
        "layout": "legacy",
        "voltage": pv1_voltage,
        "current": total_current,
        "power": total_power,
        "total_power": total_power,
        "pv1_voltage": pv1_voltage,
        "pv1_current": pv1_current,
        "pv1_power": pv1_power,
        "pv2_voltage": pv2_voltage,
        "pv2_current": pv2_current,
        "pv2_power": pv2_power,
        "pv3_voltage": pv3_voltage,
        "pv3_current": pv3_current,
        "pv3_power": pv3_power,
    }


def pv_is_aggregated(block: Any) -> bool:
    voltage = number(nested(block, 0, 0))
    string1_current = number(nested(block, 0, 1))
    string1_power = number(nested(block, 0, 2))
    aggregate_current = number(nested(block, 1, 0))
    aggregate_power = number(nested(block, 2, 0))

    if voltage is None or voltage <= 500:
        return False
    if string1_current not in (None, 0):
        return False
    if string1_power not in (None, 0):
        return False
    if aggregate_current is None and aggregate_power is None:
        return False
    return True


def pv_is_row_aggregated(block: Any) -> bool:
    voltage = number(nested(block, 0, 0))
    current = number(nested(block, 1, 0))
    power = number(nested(block, 2, 0))

    if voltage is None or current is None or power is None:
        return False

    if number(nested(block, 0, 1)) not in (None, 0):
        return False
    if number(nested(block, 0, 2)) not in (None, 0):
        return False
    if number(nested(block, 1, 1)) not in (None, 0):
        return False
    if number(nested(block, 1, 2)) not in (None, 0):
        return False
    if number(nested(block, 2, 1)) not in (None, 0):
        return False
    if number(nested(block, 2, 2)) not in (None, 0):
        return False

    return voltage > 0 and current >= 0 and power >= 0


def extract_ac_metrics(block: Any) -> dict[str, Any]:
    voltage = scaled_number(nested(block, 0, 0), 0.1, 1)
    current = scaled_number(nested(block, 1, 0), 0.1, 1)

    slot2 = number(nested(block, 2, 0))
    slot3_primary = number(nested(block, 3, 0))
    slot3_secondary = number(nested(block, 3, 1))
    slot4 = number(nested(block, 4, 0))

    expected_apparent = None
    if voltage is not None and current is not None:
        expected_apparent = float(voltage) * float(current)

    slot2_frequency = candidate_frequency(slot2)
    slot3_frequency = candidate_frequency(slot3_primary)
    slot4_frequency = candidate_frequency(slot4)

    use_frequency_layout = False
    if slot2_frequency is not None:
        score = 0
        if slot3_secondary is not None and expected_apparent is not None:
            tolerance = max(50.0, expected_apparent * 0.35)
            if abs(slot3_secondary - expected_apparent) <= tolerance:
                score += 2
            score += 1
        if slot4 is not None and slot4 >= 0:
            score += 1
        use_frequency_layout = score >= 1

    layout = "power_index_2"
    frequency = None
    active_power = None
    apparent_power = None
    total_power = None

    if use_frequency_layout:
        layout = "frequency_index_2"
        frequency = slot2_frequency
        active_power = slot3_primary
        apparent_power = slot3_secondary
        total_power = slot4 if slot4 not in (None, 0) else slot3_primary
    else:
        active_power = slot2 if slot2 is not None else slot3_primary
        frequency = slot3_frequency or slot4_frequency
        apparent_power = slot3_secondary
        total_power = slot4 if slot4 not in (None, 0) else active_power

    return {
        "layout": layout,
        "voltage": voltage,
        "current": current,
        "frequency": frequency,
        "power": round_number(active_power, 0),
        "apparent_power": round_number(apparent_power, 0),
        "total_power": round_number(total_power, 0),
    }


def candidate_frequency(value: float | int | None) -> float | None:
    if value is None:
        return None

    raw = float(value)
    for divisor in (100.0, 10.0, 1.0):
        candidate = raw / divisor
        if 40.0 < candidate < 70.0:
            return round(candidate, 2)
    return None


def extract_source_backed_power_metrics(inverter: dict[str, Any]) -> dict[str, Any]:
    type_id = integer(inverter.get("Type"))
    subtype_id = integer(inverter.get("SubType"))

    pow_dtp = _text_value(inverter.get("powDTp"))
    grid_meter_mode = _text_value(inverter.get("GrSMtr"))
    feed_to_grid = _text_value(inverter.get("Fp2Gd"))
    charge_source_priority = _text_value(inverter.get("cSPri"))
    max_charge_current_mode = _text_value(inverter.get("MCCur"))
    operating_mode = _text_value(inverter.get("OperM"))
    parallel_enable = _text_value(inverter.get("DParEn"))
    master_slave = _text_value(inverter.get("MstSlv"))
    work_mode = integer(inverter.get("workM"))

    pv_total_power, pv_branch = _pv_power(inverter, type_id, subtype_id, grid_meter_mode, pow_dtp)
    load_power, load_branch = _ac_total_out_active_power(inverter, type_id, subtype_id, pow_dtp)
    load_total_power, load_total_branch = _total_output_power(inverter)
    if load_total_power in (None, 0) and load_power is not None:
        load_total_power = load_power
        load_total_branch = f"{load_total_branch} -> fallback ACout active power"

    battery_power, battery_branch = _ems_power(inverter, type_id, subtype_id, pow_dtp)
    generator_power, generator_branch = _generator_power(inverter, type_id, subtype_id, pow_dtp)
    smart_load_power, smart_load_branch = _smart_load_power(inverter, type_id, subtype_id, pow_dtp)
    grid_power, grid_branch = _ac_total_in_power(
        inverter,
        type_id,
        subtype_id,
        charge_source_priority,
        max_charge_current_mode,
        operating_mode,
        parallel_enable,
        master_slave,
        feed_to_grid,
        pow_dtp,
        work_mode,
        pv_total_power,
        load_power,
        battery_power,
        generator_power,
    )

    return {
        "pv_total_power": round_number(pv_total_power, 0),
        "load_power": round_number(load_power, 0),
        "load_total_power": round_number(load_total_power, 0),
        "grid_power": round_number(grid_power, 0),
        "grid_total_power": round_number(grid_power, 0),
        "generator_power": round_number(generator_power, 0),
        "generator_total_power": round_number(generator_power, 0),
        "smart_load_power": round_number(smart_load_power, 0),
        "smart_load_total_power": round_number(smart_load_power, 0),
        "battery_power": round_number(battery_power, 0),
        "branches": {
            "pv_total_power": pv_branch,
            "load_power": load_branch,
            "load_total_power": load_total_branch,
            "grid_power": grid_branch,
            "generator_power": generator_branch,
            "smart_load_power": smart_load_branch,
            "battery_power": battery_branch,
        },
    }


def _text_value(value: Any) -> str:
    return coerce_string(value) or ""


def _matrix_value(matrix: Any, row: int, column: int, default: float = 0.0) -> float:
    raw = number(nested(matrix, row, column))
    if raw is None:
        return default
    return float(raw)


def _matrix_row_sum(matrix: Any, row: int, *, parse_type: str | None = None) -> float:
    values = nested(matrix, row)
    if not isinstance(values, list):
        return 0.0

    total = 0.0
    for value in values:
        raw = number(value)
        if raw is None:
            continue
        total += _number_to_symbol(raw, parse_type)
    return total


def _number_to_symbol(value: float, parse_type: str | None) -> float:
    integer_value = int(value)
    if parse_type == "1":
        integer_value &= 0xFF
        if integer_value >= 0x80:
            integer_value -= 0x100
        return float(integer_value)
    if parse_type == "2":
        integer_value &= 0xFFFF
        if integer_value >= 0x8000:
            integer_value -= 0x10000
        return float(integer_value)
    if parse_type == "3":
        integer_value &= 0xFFFFFFFF
        if integer_value >= 0x80000000:
            integer_value -= 0x100000000
        return float(integer_value)
    return float(value)


def _format_value(value: float, magnification: int = 0, precision: int = 2) -> float:
    scale = 10 ** abs(magnification)
    if magnification > 0:
        result = value * scale
    elif magnification < 0:
        result = value / scale
    else:
        result = value
    return round(result, precision)


def _has_version_stat_list(stat_list: Any) -> bool:
    return isinstance(stat_list, list) and len(stat_list) >= 2


def _is_8k_model(stat_list: Any) -> bool:
    if not _has_version_stat_list(stat_list):
        return False
    return _format_value(_matrix_value(stat_list, 1, 1, default=1.0), 0, 1) == 0.0


def _is_device_ivem(type_id: int | None) -> bool:
    return type_id == 80


def _is_device_ivem1046(type_id: int | None, subtype_id: int | None) -> bool:
    return type_id == 80 and subtype_id == 1046


def _is_device_ivem4024_v1(type_id: int | None, subtype_id: int | None) -> bool:
    return type_id == 80 and subtype_id == 518


def _is_device_ivem6048_v1(type_id: int | None, subtype_id: int | None) -> bool:
    return type_id == 80 and subtype_id == 1035


def _is_device_ivem_v1(type_id: int | None, subtype_id: int | None) -> bool:
    return type_id == 80 and subtype_id == 1039


def _is_device_ivbm(type_id: int | None, subtype_id: int | None) -> bool:
    return type_id == 80 and subtype_id in {17422, 17426}


def _is_device_ivpm(type_id: int | None) -> bool:
    return type_id == 17


def _is_device_ivgm(type_id: int | None) -> bool:
    return type_id == 81


def _is_device_ivam(type_id: int | None) -> bool:
    return type_id == 86


def _is_device_ivcm(type_id: int | None) -> bool:
    return type_id == 83


def _is_device_ivdm(type_id: int | None) -> bool:
    return type_id == 88


def _is_device_ms(type_id: int | None) -> bool:
    return type_id == 113


def _is_device_to_frequency(type_id: int | None) -> bool:
    return type_id == 16


def _is_device_20k(type_id: int | None) -> bool:
    return type_id == 84


def _is_device_50k_base(type_id: int | None) -> bool:
    return type_id == 82


def _is_device_50k_v2(type_id: int | None) -> bool:
    return type_id == 85


def _is_device_50k(type_id: int | None) -> bool:
    return _is_device_50k_base(type_id) or _is_device_50k_v2(type_id)


def _is_device_6k(type_id: int | None, subtype_id: int | None) -> bool:
    return type_id == 337 and subtype_id == 1056


def _is_device_15k(type_id: int | None, subtype_id: int | None) -> bool:
    return type_id == 337 and subtype_id == 1052


def _is_device_25k(type_id: int | None, subtype_id: int | None) -> bool:
    return type_id == 337 and subtype_id == 12849


def _is_device_8k(type_id: int | None, subtype_id: int | None) -> bool:
    return (
        (type_id == 337 and subtype_id in {1039, 1040, 1088})
        or _is_device_ivam(type_id)
    )


def _is_device_50k8k15k(type_id: int | None, subtype_id: int | None) -> bool:
    return (
        _is_device_50k(type_id)
        or _is_device_8k(type_id, subtype_id)
        or _is_device_15k(type_id, subtype_id)
        or _is_device_6k(type_id, subtype_id)
    )


def _is_ivem_can_feed(type_id: int | None, subtype_id: int | None) -> bool:
    return type_id == 80 and subtype_id in {20998, 21514, 21519, 21526}


def _is_pow_dtp(pow_dtp: str) -> bool:
    return pow_dtp == "1"


def _is_cp_show_type(
    type_id: int | None,
    subtype_id: int | None,
    operating_mode: str,
    parallel_enable: str,
    master_slave: str,
) -> bool:
    if _is_device_8k(type_id, subtype_id):
        return operating_mode == "2"

    if (
        _is_device_15k(type_id, subtype_id)
        or _is_device_20k(type_id)
        or _is_device_50k(type_id)
        or _is_device_25k(type_id, subtype_id)
    ) and operating_mode == "2":
        if parallel_enable == "0":
            return True
        if parallel_enable == "1" and master_slave == "0":
            return True

    return False


def _pv_power(
    inverter: dict[str, Any],
    type_id: int | None,
    subtype_id: int | None,
    grid_meter_mode: str,
    pow_dtp: str,
) -> tuple[float, str]:
    parse_type = "2" if _is_device_ms(type_id) else None
    row = 3 if (_is_pow_dtp(pow_dtp) or _is_device_ivem4024_v1(type_id, subtype_id)) else 2
    branch = f"sum(PV[{row}])"
    value = _matrix_row_sum(inverter.get("PV"), row, parse_type=parse_type)

    if _is_device_50k(type_id) and grid_meter_mode == "1":
        value += _matrix_value(inverter.get("GrCTPP"), 2, 0)
        branch = f"{branch} + GrCTPP[2][0]"

    return _format_value(value, 0, 2), branch


def _ac_total_out_active_power(
    inverter: dict[str, Any],
    type_id: int | None,
    subtype_id: int | None,
    pow_dtp: str,
) -> tuple[float, str]:
    branch = "ACout[3][0]"
    value = _matrix_value(inverter.get("ACout"), 3, 0)
    stat_list = inverter.get("StatLst")

    if _is_device_8k(type_id, subtype_id) and _has_version_stat_list(stat_list):
        if _is_8k_model(stat_list):
            branch = "ACout[4][0]"
            value = _matrix_value(inverter.get("ACout"), 4, 0)
        else:
            branch = "ACout[4][0] + ACout[4][1]"
            value = _matrix_value(inverter.get("ACout"), 4, 0) + _matrix_value(inverter.get("ACout"), 4, 1)
    elif _is_device_ivem4024_v1(type_id, subtype_id):
        branch = "ACout[3][2]"
        value = _matrix_value(inverter.get("ACout"), 3, 2)

    if _is_pow_dtp(pow_dtp) or _is_device_ivem4024_v1(type_id, subtype_id):
        return _matrix_value(inverter.get("ACout"), 3, 2), "powDTp/IVEM4024V1 -> ACout[3][2]"

    return value, branch


def _total_output_power(inverter: dict[str, Any]) -> tuple[float, str]:
    value = _number_to_symbol(_matrix_value(inverter.get("ACout"), 2, 4), "2")
    return value, "ACout[2][4]"


def _generator_power(
    inverter: dict[str, Any],
    type_id: int | None,
    subtype_id: int | None,
    pow_dtp: str,
) -> tuple[float, str]:
    branch = "GEN[3][0]"
    value = _matrix_value(inverter.get("GEN"), 3, 0)
    stat_list = inverter.get("StatLst")

    if _is_device_8k(type_id, subtype_id):
        if _has_version_stat_list(stat_list):
            if _is_8k_model(stat_list):
                branch = "GEN[4][0]"
                value = _matrix_value(inverter.get("GEN"), 4, 0)
            else:
                branch = "GEN[4][0] + GEN[4][1]"
                value = _matrix_value(inverter.get("GEN"), 4, 0) + _matrix_value(inverter.get("GEN"), 4, 1)

    if _is_pow_dtp(pow_dtp) or _is_device_ivem4024_v1(type_id, subtype_id):
        return _matrix_value(inverter.get("GEN"), 3, 1), "powDTp/IVEM4024V1 -> GEN[3][1]"

    if _is_device_ivem6048_v1(type_id, subtype_id) or _is_device_ivem_v1(type_id, subtype_id):
        return _matrix_value(inverter.get("GEN"), 4, 0), "IVEM6048_V1/IVEM_V1 -> GEN[4][0]"

    return value, branch


def _smart_load_power(
    inverter: dict[str, Any],
    type_id: int | None,
    subtype_id: int | None,
    pow_dtp: str,
) -> tuple[float, str]:
    branch = "GEN[3][0]"
    value = _matrix_value(inverter.get("GEN"), 3, 0)
    stat_list = inverter.get("StatLst")

    if _is_device_ivam(type_id):
        branch = "SmartL[3][0]"
        value = _matrix_value(inverter.get("SmartL"), 3, 0)
    elif _is_device_8k(type_id, subtype_id):
        if _has_version_stat_list(stat_list):
            if _is_8k_model(stat_list):
                branch = "GEN[4][0]"
                value = _matrix_value(inverter.get("GEN"), 4, 0)
            else:
                branch = "GEN[4][0] + GEN[4][1]"
                value = _matrix_value(inverter.get("GEN"), 4, 0) + _matrix_value(inverter.get("GEN"), 4, 1)
    elif _is_device_ivem_v1(type_id, subtype_id) or _is_device_ivbm(type_id, subtype_id) or _is_device_ivem1046(type_id, subtype_id):
        branch = "SmartL[4][0]"
        value = _matrix_value(inverter.get("SmartL"), 4, 0)
    elif _is_device_ivem4024_v1(type_id, subtype_id):
        branch = "SmartL[4][1]"
        value = _matrix_value(inverter.get("SmartL"), 4, 1)
    elif _is_device_ivpm(type_id):
        branch = "SmartL[3][0]"
        value = _matrix_value(inverter.get("SmartL"), 3, 0)

    if _is_pow_dtp(pow_dtp):
        return _matrix_value(inverter.get("SmartL"), 3, 1), "powDTp -> SmartL[3][1]"

    if _is_device_ivem6048_v1(type_id, subtype_id) or _is_device_ivem_v1(type_id, subtype_id):
        return _matrix_value(inverter.get("GEN"), 4, 0), "IVEM6048_V1/IVEM_V1 -> GEN[4][0]"

    return value, branch


def _ems_power(
    inverter: dict[str, Any],
    type_id: int | None,
    subtype_id: int | None,
    pow_dtp: str,
) -> tuple[float, str]:
    batt_matrix = inverter.get("Batt2") or inverter.get("Batt")
    branch = "Batt[2][0]"
    value = _matrix_value(batt_matrix, 2, 0)

    if _is_device_50k8k15k(type_id, subtype_id) or _is_device_20k(type_id):
        branch = "Batt[2][0] + Batt[2][1]"
        value = _matrix_value(batt_matrix, 2, 0) + _matrix_value(batt_matrix, 2, 1)

    if _is_pow_dtp(pow_dtp) or _is_device_ivem4024_v1(type_id, subtype_id):
        return _matrix_value(batt_matrix, 2, 1), "powDTp/IVEM4024V1 -> Batt[2][1]"

    return value, branch


def _ac_total_in_inv_power(
    inverter: dict[str, Any],
    type_id: int | None,
    subtype_id: int | None,
    charge_source_priority: str,
    max_charge_current_mode: str,
    operating_mode: str,
    parallel_enable: str,
    master_slave: str,
    pow_dtp: str,
    work_mode: int | None,
    pv_total_power: float,
    load_power: float,
    battery_power: float,
    generator_power: float,
) -> tuple[float, str]:
    branch = "ACin[3][0]"
    value = _matrix_value(inverter.get("ACin"), 3, 0)

    if _is_pow_dtp(pow_dtp) or _is_device_ivem4024_v1(type_id, subtype_id):
        branch = "powDTp/IVEM4024V1 -> ACin[3][1]"
        value = _matrix_value(inverter.get("ACin"), 3, 1)
    elif _is_device_ivem6048_v1(type_id, subtype_id) or _is_device_ivem_v1(type_id, subtype_id):
        branch = "IVEM6048_V1/IVEM_V1 -> ACin[4][1]"
        value = _matrix_value(inverter.get("ACin"), 4, 1)

    stat_list = inverter.get("StatLst")
    if _is_device_8k(type_id, subtype_id) and _has_version_stat_list(stat_list):
        if _is_8k_model(stat_list):
            return _matrix_value(inverter.get("ACin"), 4, 0), "8K -> ACin[4][0]"
        return (
            _matrix_value(inverter.get("ACin"), 4, 0) + _matrix_value(inverter.get("ACin"), 4, 1),
            "8K -> ACin[4][0] + ACin[4][1]",
        )

    if _is_device_to_frequency(type_id):
        if work_mode == 3:
            return 0.0, "ToFrequency workM=3 -> 0"
        if work_mode in {4, 5} and value == 0:
            if charge_source_priority == "3" or max_charge_current_mode == "0":
                return _matrix_value(inverter.get("ACout"), 3, 0), "ToFrequency fallback -> ACout[3][0]"
            return load_power + battery_power - pv_total_power, "ToFrequency fallback -> load + battery - pv"

    if (
        _is_device_ivem(type_id)
        and not pow_dtp
        and not _is_device_ivbm(type_id, subtype_id)
        and not _is_ivem_can_feed(type_id, subtype_id)
        and work_mode in {2, 5}
        and value == 0
    ):
        generator_present = generator_power != 0
        if not (
            (_is_device_ivem4024_v1(type_id, subtype_id) or _is_device_ivem_v1(type_id, subtype_id) or _is_device_ivem6048_v1(type_id, subtype_id))
            and generator_present
        ):
            fallback_battery_power = battery_power
            fallback_branch = "IVEM fallback -> load + battery - pv"
            if work_mode == 5:
                fallback_battery_power = max(battery_power, 0.0)
                fallback_branch = "IVEM workM=5 fallback -> load + max(battery, 0) - pv"

            fallback = load_power + fallback_battery_power - pv_total_power
            if fallback >= 50:
                return fallback, fallback_branch

    return value, branch


def _ac_total_in_power(
    inverter: dict[str, Any],
    type_id: int | None,
    subtype_id: int | None,
    charge_source_priority: str,
    max_charge_current_mode: str,
    operating_mode: str,
    parallel_enable: str,
    master_slave: str,
    feed_to_grid: str,
    pow_dtp: str,
    work_mode: int | None,
    pv_total_power: float,
    load_power: float,
    battery_power: float,
    generator_power: float,
) -> tuple[float, str]:
    value, branch = _ac_total_in_inv_power(
        inverter,
        type_id,
        subtype_id,
        charge_source_priority,
        max_charge_current_mode,
        operating_mode,
        parallel_enable,
        master_slave,
        pow_dtp,
        work_mode,
        pv_total_power,
        load_power,
        battery_power,
        generator_power,
    )

    if _is_cp_show_type(type_id, subtype_id, operating_mode, parallel_enable, master_slave):
        grctpp_values = nested(inverter.get("GrCTPP"), 0)
        total = 0.0
        if isinstance(grctpp_values, list):
            limit = 1 if (_is_device_8k(type_id, subtype_id) and _is_8k_model(inverter.get("StatLst"))) else 2 if _is_device_8k(type_id, subtype_id) else 3
            for item in grctpp_values[:limit]:
                raw = number(item)
                if raw is not None:
                    total += float(raw)

        magnification = 0
        if _is_device_20k(type_id) or _is_device_50k_v2(type_id):
            magnification = 1
        elif not _is_device_8k(type_id, subtype_id):
            magnification = 2
        value = _format_value(total, magnification, 2)
        branch = f"cp_show_type -> sum(GrCTPP[0][:{1 if (_is_device_8k(type_id, subtype_id) and _is_8k_model(inverter.get('StatLst'))) else 2 if _is_device_8k(type_id, subtype_id) else 3}])"

    if feed_to_grid == "1":
        return value, branch
    if value < 0:
        return 0.0, f"{branch} -> clamp negative"
    return value, branch