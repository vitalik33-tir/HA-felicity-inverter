from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging
from time import monotonic
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import FelicityApiError, FelicityClient
from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_SCAN_INTERVAL,
    PLATFORMS,
)
from .persistent_energy import PersistentEnergyAccumulator
from .telemetry import normalize_telemetry

_LOGGER = logging.getLogger(__name__)
PERSISTENT_ENERGY_STORAGE_VERSION = 1
PERSISTENT_ENERGY_SAVE_DELAY = 30


@dataclass(slots=True)
class FelicityRuntimeData:
    """Runtime objects stored for a config entry."""

    client: FelicityClient
    coordinator: DataUpdateCoordinator[dict[str, Any]]
    persistent_energy_store: Store[dict[str, Any]]
    persistent_energy_accumulator: PersistentEnergyAccumulator


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up Felicity Inverter from YAML (unused)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a Felicity Inverter config entry."""
    host = _entry_value(entry, CONF_HOST)
    port = _entry_int_value(entry, CONF_PORT, DEFAULT_PORT)
    scan_interval = max(
        _entry_int_value(entry, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        MIN_SCAN_INTERVAL,
    )

    if host is None:
        raise UpdateFailed("Missing host configuration")

    client = FelicityClient(host, port)
    persistent_energy_store = Store[dict[str, Any]](
        hass,
        PERSISTENT_ENERGY_STORAGE_VERSION,
        f"{DOMAIN}_{entry.entry_id}_persistent_energy",
    )
    persistent_energy_accumulator = PersistentEnergyAccumulator(
        max_gap_seconds=max(float(scan_interval * 3), float(scan_interval + 5)),
    )
    persistent_energy_accumulator.restore(await persistent_energy_store.async_load())

    async def _async_update_data() -> dict[str, Any]:
        try:
            raw_data = await client.async_fetch_data()
            telemetry = normalize_telemetry(raw_data, host=host, port=port)
            telemetry.update(
                persistent_energy_accumulator.apply_sample(
                    telemetry,
                    sampled_at_monotonic=monotonic(),
                )
            )
            persistent_energy_store.async_delay_save(
                persistent_energy_accumulator.snapshot,
                PERSISTENT_ENERGY_SAVE_DELAY,
            )
            return telemetry
        except FelicityApiError as err:
            raise UpdateFailed(str(err)) from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{entry.entry_id}",
        update_method=_async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = FelicityRuntimeData(
        client=client,
        coordinator=coordinator,
        persistent_energy_store=persistent_energy_store,
        persistent_energy_accumulator=persistent_energy_accumulator,
    )

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Felicity Inverter config entry."""
    runtime = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if runtime is not None:
        await runtime.persistent_energy_store.async_save(
            runtime.persistent_energy_accumulator.snapshot()
        )

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok and DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the integration when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


def _entry_value(entry: ConfigEntry, key: str, default: Any = None) -> Any:
    return entry.options.get(key, entry.data.get(key, default))


def _entry_int_value(entry: ConfigEntry, key: str, default: int) -> int:
    value = _entry_value(entry, key, default)
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
