"""Support for Exohome Fan."""
import asyncio
from typing import Any

from homeassistant.components.fan import (
    FanEntityFeature,
    FanEntity
)

from .core.const import (
    DEVICE_TYPE_AIRPURIFIER,
    DEVICE_TYPE_FAN,
    FAN_OPERATING_MODE,
    FAN_OSCILLATE,
    FAN_POWER,
    FAN_PRESET_MODES,
    FAN_SPEED,
    AIRPURIFIER_OPERATING_MODE,
    AIRPURIFIER_PICOPURE,
    AIRPURIFIER_PRESET_MODES
)

from .coordinator import ExohomeDataUpdateCoordinator
from .entity import ExohomeEntity
from .const import (
    DOMAIN,
    LOGGER
)


SAMPO_FAN_TYPE = [DEVICE_TYPE_AIRPURIFIER, DEVICE_TYPE_FAN]

def get_key_from_dict(dictionary, value):
    """ get key from dictionary by value"""
    return list(dictionary.keys())[list(
                    dictionary.values()).index(value)]


async def async_setup_entry(hass, entry, async_add_entities) -> bool:
    """Set up Exohome Fans based on a config entry."""
    coordinator: ExohomeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    devices = coordinator.data
    if ((isinstance(devices, dict) and len(devices) <= 1) or (devices is None)):
        return

    try:
        entities = []

        for device, info in devices.items():
            if info.get("properties", None):
                device_id = int(info.get("properties", None)["profile"]["esh"]["device_id"])
                if device_id in SAMPO_FAN_TYPE:
                    entities.extend(
                        [ExohomeFan(
                            coordinator, device, info)]
                    )

        async_add_entities(entities)
    except AttributeError as ex:
        LOGGER.error(ex)

    return True


class ExohomeFan(ExohomeEntity, FanEntity):
    """Define a Exohome Fan."""

    def __init__(
        self,
        coordinator,
        device,
        info
    ):
        super().__init__(coordinator, device, info)
        self._attr_speed_count = 100
        self._state = False
        if self._device_id == DEVICE_TYPE_FAN:
            self._attr_speed_count = 15
        if self._device_id == DEVICE_TYPE_AIRPURIFIER:
            self._attr_speed_count = 5

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        feature = FanEntityFeature.SET_SPEED | FanEntityFeature.TURN_OFF | FanEntityFeature.TURN_ON
        status = self.coordinator.data[self.device]["properties"]["status"]

        if self._device_id == DEVICE_TYPE_FAN:
            if status.get(FAN_OPERATING_MODE, None) is not None:
                feature |= FanEntityFeature.PRESET_MODE

            if status.get(FAN_OSCILLATE, None) is not None:
                feature |= FanEntityFeature.OSCILLATE

        if self._device_id == DEVICE_TYPE_AIRPURIFIER:
            if status.get(AIRPURIFIER_PICOPURE, None) is not None:
                feature |= FanEntityFeature.PRESET_MODE

        return feature

    @property
    def is_on(self):
        """Return true if device is on."""
        status = self.coordinator.data[self.device]["properties"]["status"]

        self._state = bool(int(status.get(FAN_POWER, 0)))

        return self._state

    @property
    def percentage(self) -> int | None:
        """Return the current speed."""
        status = self.coordinator.data[self.device]["properties"]["status"]

        is_on = bool(int(status.get(FAN_POWER, 0)))

        value = 0
        if is_on:
            if status.get(FAN_OPERATING_MODE, None) is None:
                LOGGER.error("Can not get status!")
                return 0

            if self._device_id == DEVICE_TYPE_FAN:
                value = int(status.get(FAN_SPEED))
            if self._device_id == DEVICE_TYPE_AIRPURIFIER:
                value = int(
                    status.get(AIRPURIFIER_OPERATING_MODE) * self.percentage_step)
            return value
        return value

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn the device on."""
        if preset_mode:
            # If operation mode was set the device must not be turned on.
            await self.async_set_preset_mode(preset_mode)
        else:
            await self.client.set_device(self.device, FAN_POWER, 1)
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        await self.client.set_device(self.device, FAN_POWER, 0)
        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()

    @property
    def preset_modes(self) -> list[str] | None:
        """Get the list of available preset modes."""
        modes = []
        if self._device_id == DEVICE_TYPE_FAN:
            modes = list(FAN_PRESET_MODES.keys())
        if self._device_id == DEVICE_TYPE_AIRPURIFIER:
            for field in self.fields:
                if AIRPURIFIER_PICOPURE == field:
                    modes.append(AIRPURIFIER_PRESET_MODES[field])
        return modes

    @property
    def preset_mode(self) -> str | None:
        """Get the current preset mode."""
        preset_mode = None
        status = self.coordinator.data[self.device]["properties"]["status"]
        if self._device_id == DEVICE_TYPE_FAN:
            value = status.get(FAN_OPERATING_MODE, 0)
            preset_mode = get_key_from_dict(FAN_PRESET_MODES, value)
        if self._device_id == DEVICE_TYPE_AIRPURIFIER:
            value = status.get(FAN_OPERATING_MODE, 0)
            for key, mode in AIRPURIFIER_PRESET_MODES.items():
                if key in status and status[key]:
                    preset_mode = mode
                    break

        return preset_mode

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        if self._device_id == DEVICE_TYPE_FAN:
            await self.client.set_device(
                self.device, FAN_OPERATING_MODE, FAN_PRESET_MODES[preset_mode])
        if self._device_id == DEVICE_TYPE_AIRPURIFIER:
            await self.client.set_device(
                self.device, FAN_OPERATING_MODE, AIRPURIFIER_PRESET_MODES[preset_mode])
        await self.coordinator.async_request_refresh()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        if percentage == 0:
            await self.client.set_device(self.device, FAN_POWER, 0)
        else:
            if self._device_id == DEVICE_TYPE_FAN:
                await self.client.set_device(self.device, FAN_SPEED, percentage)
            if self._device_id == DEVICE_TYPE_AIRPURIFIER:
                await self.client.set_device(
                    self.device, AIRPURIFIER_OPERATING_MODE, percentage / self.percentage_step)
        await self.coordinator.async_request_refresh()

    @property
    def oscillating(self) -> bool | None:
        """Return the oscillation state."""
        status = self.coordinator.data[self.device]["properties"]["status"]
        value = False
        if self._device_id == DEVICE_TYPE_FAN:
            value = bool(status.get(FAN_OSCILLATE, 0))

        return value

    async def async_oscillate(self, oscillating: bool) -> None:
        """Set oscillation."""
        if self._device_id == DEVICE_TYPE_FAN:
            await self.client.set_device(self.device, FAN_OSCILLATE, oscillating)
        await self.coordinator.async_request_refresh()
