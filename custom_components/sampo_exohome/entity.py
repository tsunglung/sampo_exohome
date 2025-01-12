"""Support for Exohome."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER
from .coordinator import ExohomeDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class ExohomeEntityDescription:
    """Define an description for Exohome entities."""



class ExohomeEntity(CoordinatorEntity[ExohomeDataUpdateCoordinator]):
    """Define a base Exohome entity."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ExohomeDataUpdateCoordinator,
        device: str,
        info: dict,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.device = device
        self.info = info
        self.coordinator = coordinator
        self.client = coordinator.get_client()

        self._device_id = int(self.info["properties"]["profile"]["esh"]["device_id"])

    @property
    def nickname(self) -> str:
        return self.info["properties"]["displayName"]

    @property
    def model(self) -> str:
        return self.info["properties"]["profile"]["esh"]["model"]

    @property
    def name(self) -> str:
        return self.info["properties"]["displayName"]

    @property
    def unique_id(self) -> str:
        return self.device

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        profile = self.info["properties"].get("profile", {})
        module = {}
        esh = {}
        if profile:
            module = profile.get("module", {})
            esh = profile.get("esh", {})
        return DeviceInfo(
            identifiers={(DOMAIN, str(self.device))},
            configuration_url="http://{}".format(module.get("local_ip", "")),
            name=self.info["properties"]["displayName"],
            manufacturer=esh.get("brand", ""),
            model=self.model,
            sw_version=module.get("firmware_version", ""),
            hw_version=esh.get("esh_version", "")
        )

    @property
    def available(self) -> bool:
        return bool(self.info["properties"]["connected"])

    @property
    def status(self) -> dict:
        return self.info["properties"].get("status", {})

    @property
    def device_status(self) -> str:
        return self.info["properties"]["device_status"]

    @property
    def fields(self) -> list:
        return self.info["properties"].get("fields",[])

    @property
    def fields_range(self) -> list:
        return self.info["properties"].get("fields_range", {})


