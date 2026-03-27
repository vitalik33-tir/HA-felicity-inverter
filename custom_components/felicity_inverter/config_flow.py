from __future__ import annotations

from typing import Any
import logging

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.data_entry_flow import FlowResult

from .api import FelicityApiError, FelicityClient
from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)
from .telemetry import normalize_telemetry

_LOGGER = logging.getLogger(__name__)


async def _validate_connection(host: str, port: int) -> dict[str, Any]:
    client = FelicityClient(host, port)
    raw_data = await client.async_fetch_data()
    return normalize_telemetry(raw_data, host=host, port=port)


class FelicityConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Felicity Inverter."""

    VERSION = 2

    @staticmethod
    def async_get_options_flow(config_entry: ConfigEntry) -> config_entries.OptionsFlow:
        """Return the options flow for this handler."""
        return FelicityOptionsFlow(config_entry)

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the initial configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = int(user_input[CONF_PORT])
            scan_interval = max(int(user_input[CONF_SCAN_INTERVAL]), MIN_SCAN_INTERVAL)

            if _host_port_in_use(self._async_current_entries(), host, port):
                return self.async_abort(reason="already_configured")

            try:
                data = await _validate_connection(host, port)
            except FelicityApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # pragma: no cover - defensive safety for HA UI
                _LOGGER.exception("Unexpected exception during Felicity config validation")
                errors["base"] = "unknown"
            else:
                unique_id = data.get("device_serial") or f"{host}:{port}"
                await self.async_set_unique_id(str(unique_id))
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_NAME: user_input[CONF_NAME],
                        CONF_HOST: host,
                        CONF_PORT: port,
                        CONF_SCAN_INTERVAL: scan_interval,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=DEFAULT_SCAN_INTERVAL,
                    ): vol.All(int, vol.Range(min=MIN_SCAN_INTERVAL)),
                }
            ),
            errors=errors,
        )


class FelicityOptionsFlow(config_entries.OptionsFlow):
    """Handle Felicity Inverter options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Manage integration options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = int(user_input[CONF_PORT])
            scan_interval = max(int(user_input[CONF_SCAN_INTERVAL]), MIN_SCAN_INTERVAL)

            entries = [
                entry
                for entry in self.hass.config_entries.async_entries(DOMAIN)
                if entry.entry_id != self._config_entry.entry_id
            ]
            if _host_port_in_use(entries, host, port):
                errors["base"] = "already_configured"
            else:
                try:
                    await _validate_connection(host, port)
                except FelicityApiError:
                    errors["base"] = "cannot_connect"
                except Exception:  # pragma: no cover - defensive safety for HA UI
                    _LOGGER.exception("Unexpected exception during Felicity options validation")
                    errors["base"] = "unknown"
                else:
                    return self.async_create_entry(
                        title="",
                        data={
                            CONF_HOST: host,
                            CONF_PORT: port,
                            CONF_SCAN_INTERVAL: scan_interval,
                        },
                    )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST,
                        default=self._config_entry.options.get(
                            CONF_HOST,
                            self._config_entry.data.get(CONF_HOST),
                        ),
                    ): str,
                    vol.Required(
                        CONF_PORT,
                        default=self._config_entry.options.get(
                            CONF_PORT,
                            self._config_entry.data.get(CONF_PORT, DEFAULT_PORT),
                        ),
                    ): int,
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=self._config_entry.options.get(
                            CONF_SCAN_INTERVAL,
                            self._config_entry.data.get(
                                CONF_SCAN_INTERVAL,
                                DEFAULT_SCAN_INTERVAL,
                            ),
                        ),
                    ): vol.All(int, vol.Range(min=MIN_SCAN_INTERVAL)),
                }
            ),
            errors=errors,
        )


def _host_port_in_use(entries: list[ConfigEntry], host: str, port: int) -> bool:
    for existing in entries:
        existing_host = existing.options.get(CONF_HOST, existing.data.get(CONF_HOST))
        existing_port = existing.options.get(CONF_PORT, existing.data.get(CONF_PORT))
        try:
            existing_port_int = int(existing_port)
        except (TypeError, ValueError):
            continue
        if existing_host == host and existing_port_int == port:
            return True
    return False
