"""Define a Sampo Exohome data coordinator."""

import asyncio
from collections.abc import Callable
from datetime import timedelta
from typing import Any
from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_TOKEN, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.ssl import get_default_context

from .core.client import Client
from .core.device import Device
from .core.errors import InvalidCredentialsError, ExohomeError
from .util import async_store_token as store_token
from .const import (
    CONF_USER_ID,
    CONF_TOKEN_EXPIRES_AT,
    DOMAIN,
    LOGGER,
)

DATA_SENSORS = "sensors"
#DATA_USER_PREFERENCES = "user_preferences"

DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)


class ExohomeDataUpdateCoordinator(DataUpdateCoordinator):
    """Define a Exohome data coordinator."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        *,
        entry: ConfigEntry,
        client: Client,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass,
            LOGGER,
            name=entry.data[CONF_USERNAME],
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self._token_expries_at = 0
        self._client = client
        self._entry = entry
        self._hass = hass
        hass.bus.async_listen(EVENT_HOMEASSISTANT_STOP, self._async_ha_stop),

    async def _async_ha_stop(self, event: Event) -> None:
        """Stop reconnecting if hass is stopping."""
        await self._client.ws_close()

    async def _async_update_data(self) -> dict:
        """Fetch data from Exohome."""
        try:
            devices = await self._client.get_all_devices()
        except InvalidCredentialsError as e:
            raise ConfigEntryAuthFailed from e
        except ExohomeError as e:
            raise UpdateFailed(
                f"There was a Exohome error while updating: {e}"
            ) from e
        email, password, expires_at = self._client.get_login_info()

        if expires_at != self._token_expries_at:
            LOGGER.error("expired")
            info = {
                CONF_PASSWORD: password,
                CONF_TOKEN: self._client.token,
                CONF_USER_ID: self._client.id,
                CONF_TOKEN_EXPIRES_AT: expires_at
            }
            await store_token(self._hass, email, info)
        return devices

    async def _async_setup(self) -> None:
        """Set up the coordinator."""
        async with asyncio.timeout(10):
            try:
                _, _, self._token_expries_at = self._client.get_login_info()
                default_context = get_default_context()
                await self._client.ws_connect(default_context)
                #devices = await self._client.get_all_devices()
            except InvalidCredentialsError as e:
                raise ConfigEntryAuthFailed from e
            except ExohomeError as e:
                raise UpdateFailed(
                    f"There was a Exohome error while updating: {e}"
                ) from e
            #else:
            #    self.data = devices

    def get_client(self) -> Client:
        """ return client"""
        return self._client
