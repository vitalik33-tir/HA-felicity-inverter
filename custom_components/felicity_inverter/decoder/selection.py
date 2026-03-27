from __future__ import annotations

from typing import Any

from ..api import RawPollData
from ..protocol import BMS_TYPE, INVERTER_TYPE
from .helpers import coerce_string


def response_objects(raw_data: RawPollData, key: str) -> list[dict[str, Any]]:
    response = raw_data.responses.get(key)
    if response is None:
        return []
    return [obj for obj in response.objects if isinstance(obj, dict)]


def merge_inverter_objects(
    objects: list[dict[str, Any]],
    inverter_serial: str | None = None,
) -> dict[str, Any]:
    primary = select_primary_inverter_object(objects, inverter_serial=inverter_serial)
    if not primary:
        return {}

    serial = inverter_serial or coerce_string(primary.get("DevSN"))
    merged: dict[str, Any] = {}
    for obj in objects:
        if belongs_to_primary_inverter(obj, serial):
            merged.update(obj)

    if not merged:
        merged.update(primary)
    return merged


def select_primary_inverter_object(
    objects: list[dict[str, Any]],
    inverter_serial: str | None = None,
) -> dict[str, Any]:
    if inverter_serial is not None:
        for obj in objects:
            if belongs_to_primary_inverter(obj, inverter_serial):
                return obj

    for obj in objects:
        if obj.get("Type") == INVERTER_TYPE:
            return obj

    for obj in objects:
        if obj.get("Type") != BMS_TYPE:
            return obj

    return objects[0] if objects else {}


def belongs_to_primary_inverter(obj: dict[str, Any], inverter_serial: str | None) -> bool:
    obj_type = obj.get("Type")
    if obj_type == BMS_TYPE:
        return False

    if inverter_serial and obj.get("DevSN") == inverter_serial:
        return True

    if obj_type == INVERTER_TYPE:
        return True

    return inverter_serial is None and obj_type is None


def collect_bms_objects(
    objects: list[dict[str, Any]],
    *,
    inverter_serial: str | None,
) -> list[dict[str, Any]]:
    return [obj for obj in objects if is_bms_object(obj, inverter_serial)]


def is_bms_object(obj: dict[str, Any], inverter_serial: str | None) -> bool:
    if obj.get("Type") == BMS_TYPE:
        return True

    if inverter_serial is None:
        return False

    return obj.get("InvSN") == inverter_serial and obj.get("DevSN") != inverter_serial