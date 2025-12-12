from __future__ import annotations
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


@dataclass
class FelicityBinarySensorDescription(BinarySensorEntityDescription):
    """Extended description for Felicity binary sensors."""


BINARY_SENSOR_DESCRIPTIONS: tuple[FelicityBinarySensorDescription, ...] = (
    FelicityBinarySensorDescription(
        key="fault_active",
        name="Fault Active",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicityBinarySensorDescription(
        key="warning_active",
        name="Warning Active",
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicityBinarySensorDescription(
        key="ac_input_present",
        name="AC Input Present",
        device_class=BinarySensorDeviceClass.POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicityBinarySensorDescription(
        key="battery_present",
        name="Battery Present",
        device_class=BinarySensorDeviceClass.POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Felicity binary sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities: list[FelicityBinarySensor] = [
        FelicityBinarySensor(coordinator, entry, desc)
        for desc in BINARY_SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities)


class FelicityBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Felicity binary sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        description: FelicityBinarySensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device info to group entities into one device."""
        data = self.coordinator.data or {}
        serial = data.get("DevSN") or data.get("wifiSN") or self._entry.entry_id
        basic = data.get("_basic") or {}
        sw_version = basic.get("version")
        host = self._entry.data.get(CONF_HOST)
        serial_display = f"{serial} ({host})" if host else serial

        inv_type = basic.get("Type") or data.get("Type")
        inv_subtype = basic.get("SubType") or data.get("SubType")
        model = "Felicity Inverter"
        if inv_type is not None and inv_subtype is not None:
            model = f"Felicity Inverter Type {inv_type} SubType {inv_subtype}"

        return {
            "identifiers": {(DOMAIN, str(serial))},
            "name": self._entry.data.get("name", "Felicity Inverter"),
            "manufacturer": "Felicity",
            "model": model,
            "sw_version": sw_version,
            "serial_number": serial_display,
        }

    @property
    def is_on(self) -> bool | None:
        data: dict = self.coordinator.data or {}
        key = self.entity_description.key

        if key == "fault_active":
            v = data.get("fault")
            return None if v is None else v != 0

        if key == "warning_active":
            v = data.get("warn")
            return None if v is None else v != 0

        def get_nested(path: tuple[Any, ...]):
            cur: Any = data
            try:
                for p in path:
                    cur = cur[p]
                return cur
            except (KeyError, IndexError, TypeError):
                return None

        if key == "ac_input_present":
            v = get_nested(("ACin", 0, 0))  # usually voltage*10
            if v is None:
                return None
            try:
                return float(v) > 50  # > 5.0V equivalent
            except Exception:
                return None

        if key == "battery_present":
            v = get_nested(("Batt", 0, 0))  # usually mV
            if v is None:
                return None
            try:
                return float(v) > 10000  # > 10V
            except Exception:
                return None

        return None
