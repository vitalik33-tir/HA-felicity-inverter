from __future__ import annotations
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


@dataclass
class FelicitySensorDescription(SensorEntityDescription):
    """Extended description for Felicity sensors."""


SENSOR_DESCRIPTIONS: tuple[FelicitySensorDescription, ...] = (
    # --- Main telemetry ---
    FelicitySensorDescription(
        key="battery_soc",
        name="Battery SOC",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery",
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="battery_voltage",
        name="Battery Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="load_percent",
        name="Load",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:gauge",
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="power_flow",
        name="Power Flow",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:flash",
    ),
    FelicitySensorDescription(
        key="bus_voltage_p",
        name="DC Bus Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
        suggested_display_precision=1,
    ),

    # --- AC input ---
    FelicitySensorDescription(
        key="ac_in_voltage",
        name="AC In Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-ac",
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="ac_in_current",
        name="AC In Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-ac",
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="ac_in_power",
        name="AC In Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower",
    ),

    # --- AC output ---
    FelicitySensorDescription(
        key="ac_out_voltage",
        name="AC Out Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-ac",
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="ac_out_current",
        name="AC Out Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-ac",
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="ac_out_power",
        name="AC Out Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-lightning-bolt",
    ),

    # --- Temperatures (Temp[0][..]) ---
    FelicitySensorDescription(
        key="temp_1",
        name="Temperature 1",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="temp_2",
        name="Temperature 2",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="temp_3",
        name="Temperature 3",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="temp_4",
        name="Temperature 4",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
        suggested_display_precision=1,
    ),

    # --- Diagnostics / codes ---
    FelicitySensorDescription(
        key="work_mode",
        name="Work Mode",
        icon="mdi:cog",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicitySensorDescription(
        key="warning_code",
        name="Warning Code",
        icon="mdi:alert",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicitySensorDescription(
        key="fault_code",
        name="Fault Code",
        icon="mdi:alert-octagon",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicitySensorDescription(
        key="firmware_version",
        name="Firmware Version",
        icon="mdi:chip",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    # --- Settings (dev set infor) ---
    FelicitySensorDescription(
        key="settings_summary",
        name="Settings Summary",
        icon="mdi:tune",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicitySensorDescription(
        key="set_operating_mode",
        name="Setting Operating Mode",
        icon="mdi:cog-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicitySensorDescription(
        key="set_ac_nominal_voltage",
        name="Setting AC Nominal Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        icon="mdi:flash",
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="set_grid_over_voltage",
        name="Setting Grid Over Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        icon="mdi:arrow-up-bold",
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="set_grid_under_voltage",
        name="Setting Grid Under Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        icon="mdi:arrow-down-bold",
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="set_grid_over_frequency",
        name="Setting Grid Over Frequency",
        native_unit_of_measurement="Hz",
        icon="mdi:waveform",
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="set_grid_under_frequency",
        name="Setting Grid Under Frequency",
        native_unit_of_measurement="Hz",
        icon="mdi:waveform",
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="set_battery_type",
        name="Setting Battery Type",
        icon="mdi:battery-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicitySensorDescription(
        key="set_battery_count",
        name="Setting Battery Count",
        icon="mdi:numeric",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicitySensorDescription(
        key="set_battery_charge_voltage",
        name="Setting Battery Charge Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        icon="mdi:battery-charging",
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="set_battery_float_voltage",
        name="Setting Battery Float Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        icon="mdi:battery",
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="set_battery_max_charge_current",
        name="Setting Battery Max Charge Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        icon="mdi:current-ac",
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="set_battery_max_discharge_current",
        name="Setting Battery Max Discharge Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        icon="mdi:current-ac",
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="set_zero_export_mode",
        name="Setting Zero Export Mode",
        icon="mdi:transmission-tower",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicitySensorDescription(
        key="set_zero_export_power",
        name="Setting Zero Export Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        icon="mdi:transmission-tower",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicitySensorDescription(
        key="set_buzzer_enabled",
        name="Setting Buzzer Enabled",
        icon="mdi:volume-high",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),

)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Felicity inverter sensors based on a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    entities: list[FelicitySensor] = [
        FelicitySensor(coordinator, entry, desc) for desc in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities)


class FelicitySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Felicity inverter sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        description: FelicitySensorDescription,
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

        model = "Felicity Inverter"
        if basic.get("Type") is not None and basic.get("SubType") is not None:
            model = f"Felicity Inverter Type {basic.get('Type')} SubType {basic.get('SubType')}"

        return {
            "identifiers": {(DOMAIN, serial)},
            "name": self._entry.data.get("name", "Felicity Inverter"),
            "manufacturer": "Felicity",
            "model": model,
            "sw_version": sw_version,
            "serial_number": serial_display,
        }

    @property
    def native_value(self) -> Any:
        data: dict = self.coordinator.data or {}
        key = self.entity_description.key

        def get_nested(path: tuple[Any, ...]):
            cur: Any = data
            try:
                for p in path:
                    cur = cur[p]
                return cur
            except (KeyError, IndexError, TypeError):
                return None

        if key == "battery_soc":
            raw = get_nested(("Batsoc", 0, 0))
            return round(raw / 100.0, 1) if isinstance(raw, (int, float)) else None

        if key == "battery_voltage":
            raw = get_nested(("Batt", 0, 0))
            return round(raw / 1000.0, 2) if isinstance(raw, (int, float)) else None

        if key == "load_percent":
            raw = data.get("lPerc")
            # Commonly appears scaled by 10 (e.g. 110 -> 11.0%)
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "power_flow":
            raw = data.get("pFlow")
            return raw if isinstance(raw, (int, float)) else None

        if key == "bus_voltage_p":
            raw = data.get("busVp")
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "ac_in_voltage":
            raw = get_nested(("ACin", 0, 0))
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "ac_in_current":
            raw = get_nested(("ACin", 1, 0))
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "ac_in_power":
            raw = get_nested(("ACin", 2, 0))
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "ac_out_voltage":
            raw = get_nested(("ACout", 0, 0))
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "ac_out_current":
            raw = get_nested(("ACout", 1, 0))
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "ac_out_power":
            raw = get_nested(("ACout", 2, 0))
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "temp_1":
            raw = get_nested(("Temp", 0, 0))
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "temp_2":
            raw = get_nested(("Temp", 0, 2))
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "temp_3":
            raw = get_nested(("Temp", 0, 3))
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "temp_4":
            raw = get_nested(("Temp", 0, 4))
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "work_mode":
            return data.get("workM")

        if key == "warning_code":
            return data.get("warn")

        if key == "fault_code":
            return data.get("fault")

        if key == "firmware_version":
            basic = data.get("_basic") or {}
            return basic.get("version")

        # --- Settings (dev set infor) ---
        settings = data.get("_settings") or {}

        if key == "settings_summary":
            return len(settings) if isinstance(settings, dict) and settings else None

        def sget(name: str):
            try:
                return settings.get(name)
            except Exception:
                return None

        if key == "set_operating_mode":
            return sget("OperM")

        if key == "set_ac_nominal_voltage":
            raw = sget("Aorvol")
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "set_grid_over_voltage":
            raw = sget("FGOV")
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "set_grid_under_voltage":
            raw = sget("FGUV")
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "set_grid_over_frequency":
            raw = sget("FGOFq")
            return round(raw / 100.0, 2) if isinstance(raw, (int, float)) else None

        if key == "set_grid_under_frequency":
            raw = sget("FGUF")
            return round(raw / 100.0, 2) if isinstance(raw, (int, float)) else None

        if key == "set_battery_type":
            return sget("batTy")

        if key == "set_battery_count":
            return sget("BNum")

        if key == "set_battery_charge_voltage":
            raw = sget("BChgV")
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "set_battery_float_voltage":
            raw = sget("BFChV")
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "set_battery_max_charge_current":
            raw = sget("BMChC")
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "set_battery_max_discharge_current":
            raw = sget("BMDCu")
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "set_zero_export_mode":
            return sget("ZEMode")

        if key == "set_zero_export_power":
            return sget("ZeroEP")

        if key == "set_buzzer_enabled":
            return sget("buzEn")

        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Expose some raw blocks as attributes for diagnostics."""
        data = self.coordinator.data or {}
        key = self.entity_description.key

        if key in ("work_mode", "warning_code", "fault_code"):
            return {
                "wan2F": data.get("wan2F"),
                "wan3F": data.get("wan3F"),
                "ParStu": data.get("ParStu"),
                "BMSFlg": data.get("BMSFlg"),
                "BFlgAll": data.get("BFlgAll"),
                "date": data.get("date"),
            }

        if key == "settings_summary":
            settings = data.get("_settings") or {}
            packs = data.get("_settings_packs") or []
            return {
                "pack_count": len(packs) if isinstance(packs, list) else None,
                "ttlPack": settings.get("ttlPack") if isinstance(settings, dict) else None,
                "last_index": settings.get("index") if isinstance(settings, dict) else None,
                "settings": settings,
            }

        return None
