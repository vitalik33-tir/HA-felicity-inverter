from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .helpers import scaled_number


@dataclass(frozen=True, slots=True)
class EnergyRowDefinition:
    prefix: str
    row_index: int
    period_indexes: dict[str, int]
    evidence: str


ENERGY_COLUMN_NOTES: dict[int, str] = {
    0: "Observed as a leading placeholder or reserved slot in every captured row so far.",
    1: "Best current candidate for the month bucket, based on flattened DTO field order.",
    2: "Strongest current candidate for the today/daily bucket, based on flattened DTO field order and sample-value shape.",
    3: "Best current candidate for the year bucket, based on flattened DTO field order.",
    4: "Best current candidate for the total bucket, based on flattened DTO field order and higher-level app summary models.",
}


SUPPORTED_ENERGY_ROWS: tuple[EnergyRowDefinition, ...] = (
    EnergyRowDefinition(
        prefix="pv_yield_energy",
        row_index=0,
        period_indexes={"monthly": 1, "daily": 2, "yearly": 3, "total": 4},
        evidence="Best-fit match to the flattened epv* family; inner-column order is inferred from DTO field order rather than a recovered raw-row consumer.",
    ),
    EnergyRowDefinition(
        prefix="load_consumption_energy",
        row_index=1,
        period_indexes={"monthly": 1, "daily": 2, "yearly": 3, "total": 4},
        evidence="Best-fit match to the flattened eload* family; inner-column order is inferred from DTO field order rather than a recovered raw-row consumer.",
    ),
)

INFERRED_ENERGY_ROWS: tuple[EnergyRowDefinition, ...] = (
    EnergyRowDefinition(
        prefix="grid_export_energy",
        row_index=2,
        period_indexes={"monthly": 1, "daily": 2, "yearly": 3, "total": 4},
        evidence="Flattened app naming includes egridFeed* / feedKwh, but the decompiled local code does not directly map Energy[row] to that family and EnergyDataRootEntity also contains acInputKwh.",
    ),
    EnergyRowDefinition(
        prefix="battery_charge_energy",
        row_index=4,
        period_indexes={"monthly": 1, "daily": 2, "yearly": 3, "total": 4},
        evidence="Flattened app naming includes ebatChar* / chargeEnergy, but no direct raw-row mapper proves that row 4 is the battery charge family rather than another aggregate.",
    ),
    EnergyRowDefinition(
        prefix="battery_discharge_energy",
        row_index=5,
        period_indexes={"monthly": 1, "daily": 2, "yearly": 3, "total": 4},
        evidence="Flattened app naming includes ebatDisChar* / disChargeEnergy, but no direct raw-row mapper proves that row 5 is the battery discharge family rather than another aggregate.",
    ),
)

UNVERIFIED_ENERGY_ROWS: tuple[tuple[int, str, dict[str, int]], ...] = (
    (
        3,
        "Row 3 is intentionally not exposed as a stable sensor family because the current codebase does not prove whether it is grid import, AC input, or another grid-side aggregate.",
        {"daily": 1, "monthly": 2, "yearly": 3, "total": 4},
    ),
    (
        8,
        "Row 8 has been observed in app UI captures, but the current decompiled sources do not prove its semantics.",
        {"daily": 1, "monthly": 2, "yearly": 3, "total": 4},
    ),
    (
        9,
        "Row 9 has been observed in app UI captures, but the current decompiled sources do not prove its semantics.",
        {"daily": 1, "monthly": 2, "yearly": 3, "total": 4},
    ),
)


def extract_energy_metrics(block: Any) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    for definition in SUPPORTED_ENERGY_ROWS:
        for period, index in definition.period_indexes.items():
            metrics[f"{definition.prefix}_{period}"] = scaled_number(
                _matrix_value(block, definition.row_index, index),
                0.001,
                3,
            )
    return metrics


def energy_decoder_status(block: Any) -> dict[str, Any]:
    return {
        "column_notes": {f"column_{column_index}": note for column_index, note in ENERGY_COLUMN_NOTES.items()},
        "supported_rows": {
            definition.prefix: _definition_status(definition, block, include_scaled_values=True)
            for definition in SUPPORTED_ENERGY_ROWS
        },
        "inferred_rows": {
            definition.prefix: _definition_status(definition, block, include_scaled_values=True)
            for definition in INFERRED_ENERGY_ROWS
        },
        "unverified_rows": {
            f"row_{row_index}": {
                "reason": reason,
                "scaled_values_kwh": _scaled_row_values(block, period_indexes, row_index),
            }
            for row_index, reason, period_indexes in UNVERIFIED_ENERGY_ROWS
        },
    }


def _definition_status(
    definition: EnergyRowDefinition,
    block: Any | None = None,
    *,
    include_scaled_values: bool = False,
) -> dict[str, Any]:
    status: dict[str, Any] = {
        "row": definition.row_index,
        "period_columns": definition.period_indexes,
        "evidence": definition.evidence,
        "raw_columns_kwh": _raw_row_values(block, definition.row_index),
    }
    if include_scaled_values:
        status["scaled_values_kwh"] = _scaled_row_values(
            block,
            definition.period_indexes,
            definition.row_index,
        )
    return status


def _scaled_row_values(
    block: Any,
    period_indexes: dict[str, int],
    row_index: int,
) -> dict[str, float | int | None]:
    return {
        period: scaled_number(_matrix_value(block, row_index, column_index), 0.001, 3)
        for period, column_index in period_indexes.items()
    }


def _raw_row_values(block: Any, row_index: int) -> dict[str, float | int | None]:
    return {
        f"column_{column_index}": scaled_number(_matrix_value(block, row_index, column_index), 0.001, 3)
        for column_index in range(5)
    }


def _matrix_value(block: Any, row_index: int, column_index: int) -> Any:
    try:
        return block[row_index][column_index]
    except (KeyError, IndexError, TypeError):
        return None