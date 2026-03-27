from __future__ import annotations

from typing import Any


def nested(value: Any, *path: Any) -> Any:
    current = value
    try:
        for part in path:
            current = current[part]
    except (KeyError, IndexError, TypeError):
        return None
    return current


def first_number(*values: Any) -> float | int | None:
    for value in values:
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return value
    return None


def first_non_zero_number(*values: Any) -> float | int | None:
    zero_candidate: float | int | None = None
    for value in values:
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            if float(value) != 0.0:
                return value
            if zero_candidate is None:
                zero_candidate = value
    return zero_candidate


def sum_numbers(*values: Any) -> float | None:
    numbers = [float(value) for value in values if isinstance(value, (int, float))]
    if not numbers:
        return None
    return sum(numbers)


def number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return None


def scaled_number(value: Any, factor: float, digits: int) -> float | None:
    raw = number(value)
    if raw is None:
        return None
    return round(raw * factor, digits)


def round_number(value: Any, digits: int) -> float | int | None:
    raw = number(value)
    if raw is None:
        return None
    if digits == 0:
        return int(round(raw))
    return round(raw, digits)


def positive_value(value: Any) -> float:
    raw = number(value)
    if raw is None:
        return 0.0
    return max(raw, 0.0)


def clamp_non_negative(value: float) -> float:
    return max(value, 0.0)


def coerce_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def map_enum(value: Any, mapping: dict[int, str]) -> str | None:
    raw = integer(value)
    if raw is None:
        return None
    return mapping.get(raw, str(raw))


def normalize_temperature(value: Any) -> float | None:
    raw = number(value)
    if raw is None:
        return None

    candidate = raw / 10.0 if abs(raw) > 100 else raw
    if -40.0 <= candidate <= 120.0:
        return round(candidate, 1)
    return None


def bit_is_set(value: int | None, bit_index: int) -> bool:
    if value is None:
        return False
    return bool(value & (1 << bit_index))