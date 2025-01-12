"""Define endpoints for interacting with devices."""

from __future__ import annotations

from typing import TYPE_CHECKING
from dataclasses import dataclass
from mashumaro import DataClassDictMixin

if TYPE_CHECKING:
    from .client import Client


@dataclass(frozen=True, kw_only=True)
class DeviceModel(DataClassDictMixin):  # pylint: disable=too-many-instance-attributes
    """Define a device."""

@dataclass(frozen=True, kw_only=True)
class DeviceAllResponse(DataClassDictMixin):
    """Define an API response containing all devices."""

    devices: list[DeviceModel]

class Device:
    """Define an object to interact with device endpoints."""

    def __init__(self, client: Client) -> None:
        """Initialize.

        Args:
        ----
            client: The exohome client

        """
        self._client = client

    async def async_all(self) -> list[DeviceModel]:
        """Get all devices.

        Returns
        -------
            A validated API response payload.

        """
#        response: DeviceAllResponse = await self._client.usesocket(
#            "get", "/phone", DeviceAllResponse)
#        return response.devices