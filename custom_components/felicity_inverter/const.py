from __future__ import annotations

from homeassistant.const import Platform

from .protocol import (
    BASIC_INFO_COMMAND,
    BMS_TYPE,
    INVERTER_TYPE,
    POLL_COMMANDS,
    REAL_INFO_COMMAND,
    SET_INFO_COMMAND,
)

DOMAIN = "felicity_inverter"

DEFAULT_NAME = "Felicity Inverter"
DEFAULT_PORT = 53970
DEFAULT_SCAN_INTERVAL = 5
MIN_SCAN_INTERVAL = 1

CONF_SCAN_INTERVAL = "scan_interval"

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]
