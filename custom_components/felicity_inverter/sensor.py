from __future__ import annotations
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from datetime import datetime
import math
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
    UnitOfEnergy,
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
        key="ac_in_frequency",
        name="AC In Frequency",
        native_unit_of_measurement="Hz",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
        suggested_display_precision=2,
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
        key="ac_out_frequency",
        name="AC Out Frequency",
        native_unit_of_measurement="Hz",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:sine-wave",
        suggested_display_precision=2,
    ),
        
    FelicitySensorDescription(
        key="ac_out_power",
        name="AC Out Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-lightning-bolt",
    ),


    # --- PV input (PV[][]) ---
    FelicitySensorDescription(
        key="pv1_voltage",
        name="PV1 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-panel",
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="pv1_current",
        name="PV1 Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="pv1_power",
        name="PV1 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
    ),

    FelicitySensorDescription(
        key="pv2_voltage",
        name="PV2 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-panel",
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="pv2_current",
        name="PV2 Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="pv2_power",
        name="PV2 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
    ),

    FelicitySensorDescription(
        key="pv3_voltage",
        name="PV3 Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-panel",
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="pv3_current",
        name="PV3 Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="pv3_power",
        name="PV3 Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
    ),

    FelicitySensorDescription(
        key="pv_total_power",
        name="PV Total Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
    ),


    # --- Energy counters (Energy[0..7] -> [0,total,day,month,year], values in Wh) ---
    # NOTE: We expose 8 groups x 4 periods. Values are converted to kWh.
    FelicitySensorDescription(
        key="energy_pv_today",
        name="PV энергия за день",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_pv_month",
        name="PV энергия за месяц",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_pv_year",
        name="PV энергия за год",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:solar-power",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_pv_total",
        name="PV энергия всего",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:solar-power",
        suggested_display_precision=2,
    ),

    FelicitySensorDescription(
        key="energy_backup_load_today",
        name="Резервная нагрузка за день",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-lightning-bolt",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_backup_load_month",
        name="Резервная нагрузка за месяц",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-lightning-bolt",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_backup_load_year",
        name="Резервная нагрузка за год",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-lightning-bolt",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_backup_load_total",
        name="Резервная нагрузка всего",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:home-lightning-bolt",
        suggested_display_precision=2,
    ),

    FelicitySensorDescription(
        key="energy_grid_import_today",
        name="Потребляемая энергия за день",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-import",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_grid_import_month",
        name="Потребляемая энергия за месяц",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-import",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_grid_import_year",
        name="Потребляемая энергия за год",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-import",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_grid_import_total",
        name="Потребляемая энергия всего",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:transmission-tower-import",
        suggested_display_precision=2,
    ),

    FelicitySensorDescription(
        key="energy_grid_export_today",
        name="Мощность питания за день",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-export",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_grid_export_month",
        name="Мощность питания за месяц",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-export",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_grid_export_year",
        name="Мощность питания за год",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:transmission-tower-export",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_grid_export_total",
        name="Мощность питания всего",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:transmission-tower-export",
        suggested_display_precision=2,
    ),

    FelicitySensorDescription(
        key="energy_battery_charge_today",
        name="Заряд АКБ за день",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-charging",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_battery_charge_month",
        name="Заряд АКБ за месяц",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-charging",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_battery_charge_year",
        name="Заряд АКБ за год",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-charging",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_battery_charge_total",
        name="Заряд АКБ всего",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:battery-charging",
        suggested_display_precision=2,
    ),

    FelicitySensorDescription(
        key="energy_battery_discharge_today",
        name="Разряд АКБ за день",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-minus",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_battery_discharge_month",
        name="Разряд АКБ за месяц",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-minus",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_battery_discharge_year",
        name="Разряд АКБ за год",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:battery-minus",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_battery_discharge_total",
        name="Разряд АКБ всего",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:battery-minus",
        suggested_display_precision=2,
    ),

    FelicitySensorDescription(
        key="energy_home_load_today",
        name="Домашняя нагрузка за день",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_home_load_month",
        name="Домашняя нагрузка за месяц",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_home_load_year",
        name="Домашняя нагрузка за год",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_home_load_total",
        name="Домашняя нагрузка всего",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:home",
        suggested_display_precision=2,
    ),

    FelicitySensorDescription(
        key="energy_total_load_today",
        name="Общая нагрузка за день",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-lightning-bolt-outline",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_total_load_month",
        name="Общая нагрузка за месяц",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-lightning-bolt-outline",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_total_load_year",
        name="Общая нагрузка за год",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:home-lightning-bolt-outline",
        suggested_display_precision=2,
    ),
    FelicitySensorDescription(
        key="energy_total_load_total",
        name="Общая нагрузка всего",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        icon="mdi:home-lightning-bolt-outline",
        suggested_display_precision=2,
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
    FelicitySensorDescription(
        key="last_update_raw",
        name="Last Update (Raw)",
        icon="mdi:clock-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
            FelicitySensorDescription(
        key="parallel_status",
        name="Parallel Status",
        icon="mdi:link-variant",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicitySensorDescription(
        key="bus_voltage_n",
        name="DC Bus Voltage N",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:current-dc",
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="telemetry_raw",
        name="Telemetry (Raw Blocks)",
        icon="mdi:code-json",
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
    FelicitySensorDescription(
        key="set_stand",
        name="Setting Stand (Stand)",
        icon="mdi:power-standby",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicitySensorDescription(
        key="set_ac_nominal_frequency_raw",
        name="Setting AC Nominal Frequency (Aorfre, raw)",
        icon="mdi:waveform",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicitySensorDescription(
        key="set_grid_over_voltage_time_raw",
        name="Setting Grid Over Voltage Time (FGOVT, raw)",
        icon="mdi:timer-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicitySensorDescription(
        key="set_grid_under_voltage_time_raw",
        name="Setting Grid Under Voltage Time (FGUVT, raw)",
        icon="mdi:timer-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicitySensorDescription(
        key="set_grid_over_frequency_time_raw",
        name="Setting Grid Over Frequency Time (FGOFqT, raw)",
        icon="mdi:timer-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicitySensorDescription(
        key="set_grid_under_frequency_time_raw",
        name="Setting Grid Under Frequency Time (FGUFT, raw)",
        icon="mdi:timer-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicitySensorDescription(
        key="set_grid_over_voltage_10min",
        name="Setting Grid Over Voltage 10min (tenGOV)",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        icon="mdi:transmission-tower",
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="set_secondary_grid_over_voltage",
        name="Setting Secondary Grid Over Voltage (sGOV)",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        icon="mdi:transmission-tower",
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="set_secondary_grid_under_voltage",
        name="Setting Secondary Grid Under Voltage (sGUV)",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        icon="mdi:transmission-tower",
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="set_generator_cooldown_time_raw",
        name="Setting Generator Cooldown Time (GCWT, raw)",
        icon="mdi:timer-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicitySensorDescription(
        key="set_generator_pv_start_delay_raw",
        name="Setting Generator PV Start Delay (GPSl, raw)",
        icon="mdi:timer-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    FelicitySensorDescription(
        key="set_battery_cv_over_grid",
        name="Setting Battery CV Over Grid (BCVOG)",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        icon="mdi:battery-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="set_battery_cv_float_grid",
        name="Setting Battery CV Float Grid (BCVFG)",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        icon="mdi:battery-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
    ),
    FelicitySensorDescription(
        key="set_battery_rv_over_grid",
        name="Setting Battery RV Over Grid (BRVOG)",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        icon="mdi:battery-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
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

        # Cache for glitch-filtering inverter-reported *_today energy counters
        self._energy_today_last_kwh: float | None = None
        self._energy_today_last_ts: datetime | None = None
        self._energy_today_last_date: str | None = None

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

        def get_nested(
            path: tuple[Any, ...],
            default: Any = None,
            *,
            scale: float | None = None,
            digits: int | None = None,
        ):
            """Safely read nested path from coordinator data.

            Args:
                path: tuple of keys/indexes
                default: value when missing
                scale: multiply numeric result by this factor
                digits: round numeric result to this amount of digits
            """
            cur: Any = data
            try:
                for p in path:
                    cur = cur[p]
            except (KeyError, IndexError, TypeError):
                return default

            if scale is not None and isinstance(cur, (int, float)):
                cur = cur * scale
            if digits is not None and isinstance(cur, (int, float)):
                cur = round(cur, digits)
            return cur

        def trunc_decimals(value: float, digits: int) -> float:
            """Truncate (not round) a float to a fixed number of decimals.

            The vendor app appears to *truncate* kWh values (e.g. 46.649 -> 46.64).
            """
            factor = 10 ** digits
            return math.trunc(value * factor) / factor

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

        if key == "ac_in_frequency":
            raw = get_nested(("ACin", 2, 0))
            return round(raw / 100.0, 2) if isinstance(raw, (int, float)) else None

        if key == "ac_in_power":
            # ACin[3][0] looks like active power in watts
            raw = get_nested(("ACin", 3, 0))
            return round(raw, 0) if isinstance(raw, (int, float)) else None

        if key == "ac_in_apparent_power":
            # ACin[3][1] looks like apparent power in volt-amperes
            raw = get_nested(("ACin", 3, 1))
            return round(raw, 0) if isinstance(raw, (int, float)) else None

        if key == "ac_out_voltage":
            raw = get_nested(("ACout", 0, 0))
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "ac_out_current":
            raw = get_nested(("ACout", 1, 0))
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "ac_out_frequency":
            raw = get_nested(("ACout", 2, 0))
            return round(raw / 100.0, 2) if isinstance(raw, (int, float)) else None

        if key == "ac_out_power":
            # ACout[3][0] looks like active power in watts
            raw = get_nested(("ACout", 3, 0))
            return round(raw, 0) if isinstance(raw, (int, float)) else None

        if key == "ac_out_apparent_power":
            raw = get_nested(("ACout", 3, 1))
            return round(raw, 0) if isinstance(raw, (int, float)) else None

        if key == "ac_out_reactive_power":
            raw = get_nested(("ACout", 3, 2))
            return round(raw, 0) if isinstance(raw, (int, float)) else None

        def _pv_is_aggregated() -> bool:
            """Detect aggregated PV layout used by some firmwares.

            Observed layouts in `real infor`:
              * Per-MPPT: PV[0]=[V1,I1,P1], PV[1]=[V2,I2,P2], PV[2]=[V3,I3,P3], PV[3]=[Ptotal]
              * Aggregated: PV[0]=[Vpv,0,0], PV[1]=[Ipv*10,0,0], PV[2]=[Ppv,0,0], PV[3]=[Ptotal]
            """
            v0 = get_nested(("PV", 0, 0))

            # Voltage is usually tens/hundreds of volts => raw > 500 (>= 50.0V).
            if not (isinstance(v0, (int, float)) and v0 > 500):
                return False

            # If PV[0][1] (current) or PV[0][2] (power) contains meaningful values,
            # assume per-MPPT layout.
            i0 = get_nested(("PV", 0, 1))
            p0 = get_nested(("PV", 0, 2))
            if isinstance(i0, (int, float)) and i0 != 0:
                return False
            if isinstance(p0, (int, float)) and p0 != 0:
                return False

            v1 = get_nested(("PV", 1, 0))
            p2 = get_nested(("PV", 2, 0))
            pt = get_nested(("PV", 3, 0))

            # Heuristic: PV[1][0] looks like current*10 (0..30A => raw 0..300)
            current_like = isinstance(v1, (int, float)) and 0 < v1 < 300

            # Heuristic: PV[2][0] is close to PV[3][0] (both are power in watts)
            power_like = (
                isinstance(pt, (int, float))
                and isinstance(p2, (int, float))
                and pt >= 0
                and p2 >= 0
                and abs(pt - p2) <= max(5.0, 0.05 * max(pt, 1.0))
                and p2 < 20000
            )

            return current_like or power_like


        if key == "pv1_voltage":
            raw = get_nested(("PV", 0, 0))
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "pv1_current":
            raw_i = get_nested(("PV", 0, 1))
            if _pv_is_aggregated():
                raw_i = get_nested(("PV", 1, 0))
            return round(raw_i / 10.0, 1) if isinstance(raw_i, (int, float)) else None

        if key == "pv1_power":
            # Some firmwares expose PV as an "aggregated" matrix:
            #   PV[0] = [Vpv, V2, V3]
            #   PV[1] = [Ipv*10, I2*10, I3*10]
            #   PV[2] = [Ppv, P2, P3]
            #   PV[3] = [Ptotal]
            # In this layout PV1 power is PV[2][0] (not PV[0][2]).
            if _pv_is_aggregated():
                p1 = get_nested(("PV", 2, 0))
                total = get_nested(("PV", 3, 0))
                if isinstance(p1, (int, float)):
                    # Some firmwares keep PV[2][0]=0 while total has value.
                    if p1 == 0 and isinstance(total, (int, float)) and total != 0:
                        return round(total, 0)
                    return round(p1, 0)
                return round(total, 0) if isinstance(total, (int, float)) else None

            # Some firmwares report PV total power only, leaving PV1 power at 0.
            # If PV2 is missing/zero, map PV1 Power to PV Total Power.
            p1 = get_nested(("PV", 0, 2))
            if isinstance(p1, (int, float)) and p1 != 0:
                return round(p1, 0)

            # PV2 considered absent when all three values are 0 (or missing)
            pv2_v = get_nested(("PV", 1, 0), default=0)
            pv2_c = get_nested(("PV", 1, 1), default=0)
            pv2_p = get_nested(("PV", 1, 2), default=0)
            total = get_nested(("PV", 3, 0))

            if (
                (not isinstance(pv2_v, (int, float)) or pv2_v == 0)
                and (not isinstance(pv2_c, (int, float)) or pv2_c == 0)
                and (not isinstance(pv2_p, (int, float)) or pv2_p == 0)
                and isinstance(total, (int, float))
            ):
                return round(total, 0)

            return round(p1, 0) if isinstance(p1, (int, float)) else (round(total, 0) if isinstance(total, (int, float)) else None)

        if key == "pv2_voltage":
            if _pv_is_aggregated():
                return 0.0
            raw = get_nested(("PV", 1, 0))
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "pv2_current":
            if _pv_is_aggregated():
                return 0.0
            raw = get_nested(("PV", 1, 1))
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "pv2_power":
            if _pv_is_aggregated():
                return 0.0
            raw = get_nested(("PV", 1, 2))
            return round(raw, 0) if isinstance(raw, (int, float)) else None

        if key == "pv3_voltage":
            if _pv_is_aggregated():
                return 0.0
            raw = get_nested(("PV", 2, 0))
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "pv3_current":
            if _pv_is_aggregated():
                return 0.0
            raw = get_nested(("PV", 2, 1))
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "pv3_power":
            if _pv_is_aggregated():
                return 0.0
            raw = get_nested(("PV", 2, 2))
            return round(raw, 0) if isinstance(raw, (int, float)) else None

        if key == "pv_total_power":
            raw = get_nested(("PV", 3, 0))
            return round(raw, 0) if isinstance(raw, (int, float)) else None

        # --- Energy counters (Energy[0..7] -> [0,total,day,month,year]) ---
        energy_map: dict[str, tuple[int, int]] = {
            # PV
            "energy_pv_total": (0, 1),
            "energy_pv_today": (0, 2),
            "energy_pv_month": (0, 3),
            "energy_pv_year": (0, 4),
            # Backup load (Reserved)
            "energy_backup_load_total": (1, 1),
            "energy_backup_load_today": (1, 2),
            "energy_backup_load_month": (1, 3),
            "energy_backup_load_year": (1, 4),
            # Grid import (consumption)
            "energy_grid_import_total": (2, 1),
            "energy_grid_import_today": (2, 2),
            "energy_grid_import_month": (2, 3),
            "energy_grid_import_year": (2, 4),
            # Grid export (feed-in)
            "energy_grid_export_total": (3, 1),
            "energy_grid_export_today": (3, 2),
            "energy_grid_export_month": (3, 3),
            "energy_grid_export_year": (3, 4),
            # Battery charge
            "energy_battery_charge_total": (4, 1),
            "energy_battery_charge_today": (4, 2),
            "energy_battery_charge_month": (4, 3),
            "energy_battery_charge_year": (4, 4),
            # Battery discharge
            "energy_battery_discharge_total": (5, 1),
            "energy_battery_discharge_today": (5, 2),
            "energy_battery_discharge_month": (5, 3),
            "energy_battery_discharge_year": (5, 4),
            # Home load
            "energy_home_load_total": (6, 1),
            "energy_home_load_today": (6, 2),
            "energy_home_load_month": (6, 3),
            "energy_home_load_year": (6, 4),
            # Total load (Backup + Home)
            "energy_total_load_total": (7, 1),
            "energy_total_load_today": (7, 2),
            "energy_total_load_month": (7, 3),
            "energy_total_load_year": (7, 4),
        }
        if key in energy_map:
            g, i = energy_map[key]
            raw = get_nested(("Energy", g, i))
            if not isinstance(raw, (int, float)):
                return None

            kwh = trunc_decimals(raw / 1000.0, 2)

            # The inverter sometimes outputs a short-lived glitch for *_today values
            # (e.g., after a nightly reboot), where "today" momentarily includes
            # yesterday's kWh. This causes large vertical spikes in HA History.
            # We suppress implausible upward jumps based on the time delta between
            # payload timestamps.
            if key.endswith("_today"):
                date_str = data.get("date")

                # Avoid mutating caches multiple times for the same payload.
                if (
                    date_str
                    and date_str == self._energy_today_last_date
                    and self._energy_today_last_kwh is not None
                ):
                    return self._energy_today_last_kwh

                ts = None
                if isinstance(date_str, str) and len(date_str) >= 14:
                    try:
                        ts = datetime.strptime(date_str[:14], "%Y%m%d%H%M%S")
                    except Exception:
                        ts = None

                if (
                    self._energy_today_last_kwh is not None
                    and self._energy_today_last_ts is not None
                    and ts is not None
                ):
                    dt = (ts - self._energy_today_last_ts).total_seconds()
                    if dt < 0:
                        dt = 0

                    # Conservative upper bound: 20 kW equivalent + 0.5 kWh margin.
                    max_kw = 20.0
                    allowed_jump = (max_kw * (dt / 3600.0)) + 0.5

                    if (kwh - self._energy_today_last_kwh) > allowed_jump:
                        # Keep previous value, but advance "seen" timestamp/date
                        # so we don't repeatedly process the same payload.
                        self._energy_today_last_ts = ts
                        self._energy_today_last_date = date_str
                        return self._energy_today_last_kwh

                # Accept new value
                if ts is not None:
                    self._energy_today_last_ts = ts
                self._energy_today_last_kwh = kwh
                self._energy_today_last_date = date_str
                return kwh

            return kwh


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

        if key == "last_update_raw":
            return data.get("date")

        if key == "warning_flags_raw":
            return data.get("wan2F")

        if key == "warning_flags2_raw":
            return data.get("wan3F")

        if key == "parallel_status":
            return data.get("ParStu")

        if key == "bus_voltage_n":
            raw = get_nested(("busVn",), scale=0.1, digits=1)
            return raw

        if key == "telemetry_raw":
            # Keep state small; details in attributes.
            return data.get("date") or "ok"

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

        
        if key == "set_stand":
            return sget("Stand")

        if key == "set_ac_nominal_frequency_raw":
            return sget("Aorfre")

        if key == "set_grid_over_voltage_time_raw":
            return sget("FGOVT")

        if key == "set_grid_under_voltage_time_raw":
            return sget("FGUVT")

        if key == "set_grid_over_frequency_time_raw":
            return sget("FGOFqT")

        if key == "set_grid_under_frequency_time_raw":
            return sget("FGUFT")

        if key == "set_grid_over_voltage_10min":
            raw = sget("tenGOV")
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "set_secondary_grid_over_voltage":
            raw = sget("sGOV")
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "set_secondary_grid_under_voltage":
            raw = sget("sGUV")
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "set_generator_cooldown_time_raw":
            return sget("GCWT")

        if key == "set_generator_pv_start_delay_raw":
            return sget("GPSl")

        if key == "set_battery_cv_over_grid":
            raw = sget("BCVOG")
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "set_battery_cv_float_grid":
            raw = sget("BCVFG")
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "set_battery_rv_over_grid":
            raw = sget("BRVOG")
            return round(raw / 10.0, 1) if isinstance(raw, (int, float)) else None

        if key == "set_battery_bddog_raw":
            return sget("BDDOG")

        if key == "set_battery_bddfg_raw":
            return sget("BDDFG")

        if key == "set_battery_brdfg_raw":
            return sget("BRDFG")

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

        if key in ("work_mode", "warning_code", "fault_code", "warning_flags_raw", "warning_flags2_raw", "parallel_status", "last_update_raw"):
            return {
                "wan2F": data.get("wan2F"),
                "wan3F": data.get("wan3F"),
                "ParStu": data.get("ParStu"),
                "BMSFlg": data.get("BMSFlg"),
                "BFlgAll": data.get("BFlgAll"),
                "date": data.get("date"),
            }


        if key == "telemetry_raw":
            return {
                "date": data.get("date"),
                "workM": data.get("workM"),
                "warn": data.get("warn"),
                "fault": data.get("fault"),
                "wan2F": data.get("wan2F"),
                "wan3F": data.get("wan3F"),
                "busVp": data.get("busVp"),
                "busVn": data.get("busVn"),
                "lPerc": data.get("lPerc"),
                "pFlow": data.get("pFlow"),
                "ACin": data.get("ACin"),
                "ACout": data.get("ACout"),
                "PV": data.get("PV"),
                "INV": data.get("INV"),
                "Energy": data.get("Energy"),
                "Temp": data.get("Temp"),
                "Batt": data.get("Batt"),
                "Batsoc": data.get("Batsoc"),
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