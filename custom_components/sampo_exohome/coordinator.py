"""Define a Sampo Exohome data coordinator."""

import asyncio
from collections.abc import Callable
from datetime import timedelta
from typing import Any
from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_USERNAME, EVENT_HOMEASSISTANT_STOP
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.ssl import get_default_context

from .core.client import Client
from .core.device import Device
from .core.errors import InvalidCredentialsError, ExohomeError
from .const import (
    DOMAIN,
    LOGGER,
    REFRESH_TOKEN_EXPIRY_TIME
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
        self.refresh_token_creation_time = 0
        self._client = client
        self._entry = entry
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
        return devices

    async def _async_setup(self) -> None:
        """Set up the coordinator."""
        async with asyncio.timeout(10):
            expiry_time = (
                self.refresh_token_creation_time
                + REFRESH_TOKEN_EXPIRY_TIME.total_seconds()
            )

            try:
                #if datetime.now().timestamp() >= expiry_time:
                #    await self._client.async_authenticate_from_credentials()
                #else:
                #    await self._client.authenticate_refresh(
                #        self.refresh_token, async_get_clientsession(self.hass)
                #    )
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
