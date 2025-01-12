"""Support for Sampo Smart Home."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import entity_registry as er

from .core.errors import InvalidCredentialsError, ExohomeError
from .coordinator import ExohomeDataUpdateCoordinator
from .util import async_get_client_with_credentials
from .const import (
    DOMAIN
)

PLATFORMS = [Platform.CLIMATE, Platform.FAN, Platform.SENSOR, Platform.SELECT, Platform.SWITCH]

DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sampo Smart Home as a config entry."""
    entry_updates: dict[str, Any] = {"data": {**entry.data}}

    if not entry.unique_id:
        entry_updates["unique_id"] = entry.data[CONF_USERNAME]

    try:
        client = await async_get_client_with_credentials(
            hass, entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD]
        )
    except InvalidCredentialsError as err:
        raise ConfigEntryAuthFailed("Invalid credentials") from err
    except ExohomeError as err:
        raise ConfigEntryNotReady("Config entry failed to load") from err

    hass.config_entries.async_update_entry(entry, **entry_updates)

    coordinator = ExohomeDataUpdateCoordinator(hass, entry=entry, client=client)
    await coordinator.async_config_entry_first_refresh()
    #await coordinator.async_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Sampo Smart Home config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
