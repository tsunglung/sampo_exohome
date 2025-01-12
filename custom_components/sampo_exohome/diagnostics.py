"""Diagnostics support for Notion."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_UNIQUE_ID, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_USER_ID
from .coordinator import ExohomeDataUpdateCoordinator

CONF_DEVICE_KEY = "device_key"
CONF_HARDWARE_ID = "hardware_id"
CONF_TITLE = "title"

TO_REDACT = {
    CONF_DEVICE_KEY,
    CONF_EMAIL,
    CONF_HARDWARE_ID,
    # Config entry title and unique ID may contain sensitive data:
    CONF_TITLE,
    CONF_UNIQUE_ID,
    CONF_USERNAME,
    CONF_USER_ID,
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: ExohomeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    return async_redact_data(
        {
            "entry": entry.as_dict(),
            "data": coordinator.data.asdict(),
        },
        TO_REDACT,
    )
