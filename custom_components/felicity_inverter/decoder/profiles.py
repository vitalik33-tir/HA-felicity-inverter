from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .helpers import integer


@dataclass(frozen=True, slots=True)
class ModelProfile:
    key: str
    label: str
    type_id: int | None = None
    subtype_id: int | None = None


def _profile(
    key: str,
    label: str,
    *,
    type_id: int | None = None,
    subtype_id: int | None = None,
) -> ModelProfile:
    return ModelProfile(key=key, label=label, type_id=type_id, subtype_id=subtype_id)


GENERIC_PROFILE = ModelProfile(key="generic", label="Generic")
EXACT_PROFILES: dict[tuple[int, int], ModelProfile] = {
    (80, 516): _profile("ivem3024", "IVEM3024", type_id=80, subtype_id=516),
    (80, 518): _profile("ivem4024_v1", "IVEM4024_V1", type_id=80, subtype_id=518),
    (80, 1034): _profile("ivem6048", "IVEM6048", type_id=80, subtype_id=1034),
    (80, 1035): _profile("ivem6048_v1", "IVEM6048_V1", type_id=80, subtype_id=1035),
    (80, 1038): _profile("ivem8048", "IVEM8048", type_id=80, subtype_id=1038),
    (80, 1039): _profile("ivem_v1", "IVEM_V1", type_id=80, subtype_id=1039),
    (80, 1046): _profile("ivem1046", "IVEM1046", type_id=80, subtype_id=1046),
    (80, 9224): _profile("ivem5048_ai100", "IVEM5048_AI100", type_id=80, subtype_id=9224),
    (80, 9230): _profile("integrated_machine", "Integrated Machine", type_id=80, subtype_id=9230),
    (80, 17422): _profile("ivbm_8048", "IVBM8048", type_id=80, subtype_id=17422),
    (80, 17426): _profile("ivbm_10048", "IVBM10048", type_id=80, subtype_id=17426),
    (80, 20998): _profile("ivem_can_feed", "IVEM Feed Variant", type_id=80, subtype_id=20998),
    (80, 21514): _profile("ivem_can_feed", "IVEM Feed Variant", type_id=80, subtype_id=21514),
    (80, 21519): _profile("ivem_can_feed", "IVEM Feed Variant", type_id=80, subtype_id=21519),
    (80, 21526): _profile("ivem_can_feed", "IVEM Feed Variant", type_id=80, subtype_id=21526),
    (81, 1036): _profile("ivgm_1036", "IVGM1036", type_id=81, subtype_id=1036),
    (81, 1042): _profile("ivgm_1042", "IVGM1042", type_id=81, subtype_id=1042),
    (81, 12818): _profile("ivgm_100600", "IVGM100600", type_id=81, subtype_id=12818),
    (16, 1037): _profile("to_frequency_1037", "ToFrequency1037", type_id=16, subtype_id=1037),
    (16, 1042): _profile("to_frequency_1042", "ToFrequency1042", type_id=16, subtype_id=1042),
    (337, 1039): _profile("8k_1039", "8K1039", type_id=337, subtype_id=1039),
    (337, 1040): _profile("8k_1040", "8K1040", type_id=337, subtype_id=1040),
    (337, 1052): _profile("15k", "15K", type_id=337, subtype_id=1052),
    (337, 1056): _profile("6k", "6K", type_id=337, subtype_id=1056),
    (337, 1088): _profile("ivgm_8k", "IVGM8K", type_id=337, subtype_id=1088),
    (337, 12849): _profile("25k", "25K", type_id=337, subtype_id=12849),
}

TYPE_PROFILES: dict[int, ModelProfile] = {
    16: _profile("to_frequency", "ToFrequency", type_id=16),
    17: _profile("ivpm", "IVPM", type_id=17),
    80: _profile("ivem", "IVEM", type_id=80),
    81: _profile("ivgm", "IVGM", type_id=81),
    82: _profile("50k_base", "50K Base", type_id=82),
    83: _profile("ivcm", "IVCM", type_id=83),
    84: _profile("20k", "20K", type_id=84),
    85: _profile("50k_v2", "50K V2", type_id=85),
    86: _profile("ivam", "IVAM", type_id=86),
    88: _profile("ivdm", "IVDM", type_id=88),
    113: _profile("ms", "MS", type_id=113),
}


def resolve_model_profile(inverter: dict[str, Any]) -> ModelProfile:
    type_id = integer(inverter.get("Type"))
    subtype_id = integer(inverter.get("SubType"))
    if type_id is None:
        return GENERIC_PROFILE

    if subtype_id is not None:
        exact_profile = EXACT_PROFILES.get((type_id, subtype_id))
        if exact_profile is not None:
            return exact_profile

    return TYPE_PROFILES.get(type_id, GENERIC_PROFILE)