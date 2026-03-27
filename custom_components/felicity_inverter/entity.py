from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


def build_device_info(entry: ConfigEntry, data: dict[str, Any]) -> DeviceInfo:
    """Build device information for the inverter."""
    serial = str(data.get("device_serial") or entry.unique_id or entry.entry_id)
    host = entry.options.get(CONF_HOST, entry.data.get(CONF_HOST))
    serial_display = f"{serial} ({host})" if host else serial

    device_type = data.get("device_type")
    device_subtype = data.get("device_subtype")
    model = "Felicity Inverter"
    profile_label = data.get("decoder_profile_label")
    if isinstance(profile_label, str) and profile_label and profile_label != "Generic":
        model = f"Felicity Inverter {profile_label}"
    elif device_type is not None and device_subtype is not None:
        model = f"Felicity Inverter Type {device_type} SubType {device_subtype}"

    return DeviceInfo(
        identifiers={(DOMAIN, serial)},
        manufacturer="Felicity",
        model=model,
        name=entry.title,
        serial_number=serial_display,
        sw_version=data.get("firmware_version"),
    )


class FelicityCoordinatorEntity(CoordinatorEntity):
    """Shared coordinator entity for Felicity platforms."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for the inverter."""
        return build_device_info(self._entry, self.coordinator.data or {})
