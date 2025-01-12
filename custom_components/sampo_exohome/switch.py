"""Support for Exohome switch."""

import asyncio
from dataclasses import dataclass

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntityDescription,
    SwitchEntity
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .core.const import (
    DEVICE_TYPE_AIRPURIFIER,
    DEVICE_TYPE_CLIMATE,
    AIRPURIFIER_BUZZER,
    AIRPURIFIER_RESET_FILTER_NOTIFY,
    CLIMATE_ANTI_MILDEW,
    CLIMATE_AUTO_CLEAN,
    CLIMATE_BUZZER
)
from .coordinator import ExohomeDataUpdateCoordinator
from .entity import ExohomeEntity, ExohomeEntityDescription
from .const import (
    DOMAIN,
    LOGGER
)


@dataclass(frozen=True, kw_only=True)
class ExohomeSwitchDescription(SwitchEntityDescription, ExohomeEntityDescription):
    """Describe a Exohome switch."""


AIRPURIFIER_SWITCHES: tuple[ExohomeSwitchDescription, ...] = (
    ExohomeSwitchDescription(
        key=AIRPURIFIER_RESET_FILTER_NOTIFY,
        name="Reset Filter Notify",
        device_class=SwitchDeviceClass.SWITCH,
        icon='mdi:volume-high'
    ),
    ExohomeSwitchDescription(
        key=AIRPURIFIER_BUZZER,
        name="Buzzer",
        device_class=SwitchDeviceClass.SWITCH,
        icon='mdi:volume-high'
    )
)

CLIMATE_SWITCHES: tuple[ExohomeSwitchDescription, ...] = (
    ExohomeSwitchDescription(
        key=CLIMATE_ANTI_MILDEW,
        name="Anti Mildew",
        device_class=SwitchDeviceClass.SWITCH,
        icon='mdi:broom'
    ),
    ExohomeSwitchDescription(
        key=CLIMATE_BUZZER,
        name="Buzzer",
        device_class=SwitchDeviceClass.SWITCH,
        icon='mdi:volume-source'
    ),
    ExohomeSwitchDescription(
        key=CLIMATE_AUTO_CLEAN,
        name="Auto Clean",
        device_class=SwitchDeviceClass.SWITCH,
        icon='mdi:broom'
    )
)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Exohome switches based on a config entry."""
    coordinator: ExohomeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    devices = coordinator.data

    if ((isinstance(devices, dict) and len(devices) <= 1) or (devices is None)):
        return

    try:
        entities = []

        for device, info in devices.items():
            properties = info.get("properties", None)
            if properties is None:
                continue

            device_id = int(properties["profile"]["esh"]["device_id"])
            fields = properties.get("fields", [])
            if device_id == DEVICE_TYPE_AIRPURIFIER:
                for description in AIRPURIFIER_SWITCHES:
                    if description.key in fields:
                        entities.extend(
                            [ExohomeSwitch(
                                coordinator, device, info, description)]
                        )

            if device_id == DEVICE_TYPE_CLIMATE:
                for description in CLIMATE_SWITCHES:
                    if description.key in fields:
                        entities.extend(
                            [ExohomeSwitch(
                                coordinator, device, info, description)]
                        )

        async_add_entities(entities)
    except AttributeError as ex:
        LOGGER.error(ex)

    return True


class ExohomeSwitch(ExohomeEntity, SwitchEntity):
    """Define a Exohome switch."""
    entity_description: ExohomeSwitchDescription

    def __init__(
        self,
        coordinator,
        device,
        info,
        description
    ):
        super().__init__(coordinator, device, info)
        self.entity_description = description

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{self.entity_description.name}"

    @property
    def unique_id(self):
        """Return the unique of the switch."""
        return f"{self.device}_{self._device_id}_{self.entity_description.key}"

    @property
    def is_on(self) -> int:
        """Return true if switch is on."""
        status = self.coordinator.data[self.device]["properties"]["status"]
        avaiable = status.get(self.entity_description.key, None)
        if avaiable is None:
            return STATE_UNAVAILABLE

        return bool(int(status[self.entity_description.key]))

    async def async_turn_on(self) -> None:
        """Turn the switch on."""
        await self.client.set_device(
            self.device, self.entity_description.key, 1)
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn the switch off."""
        await self.client.set_device(
            self.device, self.entity_description.key, 0)
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()
