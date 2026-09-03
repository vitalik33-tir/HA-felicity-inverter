from __future__ import annotations
# -*- coding: utf-8 -*-

from dataclasses import replace
from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import FelicityApiError, FelicityClient
from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
)
_LOGGER = logging.getLogger(__name__)


def _restore_energy_statistics_state_classes() -> None:
    """Keep periodic energy counters eligible for long-term statistics."""
    from . import sensor as sensor_platform

    periodic_suffixes = ("_today", "_month", "_year")
    sensor_platform.SENSOR_DESCRIPTIONS = tuple(
        replace(desc, state_class=SensorStateClass.TOTAL_INCREASING)
        if desc.key.startswith("energy_") and desc.key.endswith(periodic_suffixes)
        else desc
        for desc in sensor_platform.SENSOR_DESCRIPTIONS
    )


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up via YAML (not used)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Felicity entry from config entry."""

    host: str = entry.data["host"]
    port: int = entry.data["port"]
    client = FelicityClient(host, port)

    async def _async_update_data():
        try:
            return await client.async_get_data()
        except FelicityApiError as err:
            raise UpdateFailed(str(err)) from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{host}",
        update_method=_async_update_data,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }

    _restore_energy_statistics_state_classes()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok and DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
