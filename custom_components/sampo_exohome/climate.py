"""Support for Exohome  Climate"""

import asyncio

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVACMode,
    PRESET_NONE,
    SWING_ON,
    SWING_OFF,
    SWING_BOTH,
    SWING_VERTICAL,
    SWING_HORIZONTAL,
    ClimateEntityFeature
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfTemperature,
    ATTR_TEMPERATURE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .core.const import (
    DEVICE_TYPE_CLIMATE,
    CLIMATE_AVAILABLE_FAN_MODES,
    CLIMATE_FAN_SPEED,
    CLIMATE_OPERATING_MODE,
    CLIMATE_POWER,
    CLIMATE_MAXIMUM_TEMPERATURE,
    CLIMATE_MINIMUM_TEMPERATURE,
    CLIMATE_SWING_VERTICAL,
    CLIMATE_SWING_VERTICAL_LEVEL,
    CLIMATE_SWING_HORIZONTAL,
    CLIMATE_SWING_HORIZONTAL_LEVEL,
    CLIMATE_TARGET_TEMPERATURE,
    CLIMATE_TEMPERATURE_INDOOR,
    CLIMATE_TEMPERATURE_STEP
)
from .coordinator import ExohomeDataUpdateCoordinator
from .entity import ExohomeEntity
from .const import (
    DOMAIN,
    CLIMATE_AVAILABLE_PRESET_MODES,
    CLIMATE_AVAILABLE_MODES,
    LOGGER
)


def get_key_from_dict(dictionary, value):
    """ get key from dictionary by value"""
    return list(dictionary.keys())[list(
                    dictionary.values()).index(value)]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Exohome sensors based on a config entry."""
    coordinator: ExohomeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    devices = coordinator.data

    try:
        entities = []

        for device, info in devices.items():
            properties = info.get("properties", None)
            if properties:
                device_id = int(properties["profile"]["esh"]["device_id"])
                if device_id == DEVICE_TYPE_CLIMATE:
                    entities.extend(
                        [ExohomeClimate(
                            coordinator, device, info)]
                    )

        async_add_entities(entities)
    except AttributeError as ex:
        LOGGER.error(ex)

    return True


class ExohomeClimate(ExohomeEntity, ClimateEntity):
    """Define a Exohome climate."""
    _swing_mode = SWING_OFF
    _swing_vertical_level = 0
    _swing_horizontal_level = 0

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        feature = ClimateEntityFeature.TARGET_TEMPERATURE
        status = self.status

        if (status.get(CLIMATE_SWING_VERTICAL, None) or
            (status.get(CLIMATE_SWING_HORIZONTAL, None)) or
            (status.get(CLIMATE_SWING_VERTICAL_LEVEL, None)) or
            (status.get(CLIMATE_SWING_HORIZONTAL_LEVEL, None))
        ):
            feature |= ClimateEntityFeature.SWING_MODE

        if status.get(CLIMATE_FAN_SPEED, None):
            feature |= ClimateEntityFeature.FAN_MODE

        preset_mode = False
        for stts in status:
            if stts in CLIMATE_AVAILABLE_PRESET_MODES:
                preset_mode = True
                break
        if preset_mode:
            feature |= ClimateEntityFeature.PRESET_MODE

        return feature

    @property
    def temperature_unit(self) -> str:
        """ Temperature Unit """
        return UnitOfTemperature.CELSIUS

    @property
    def hvac_mode(self) -> str:
        """Return hvac operation ie. heat, cool mode."""
        status = self.coordinator.data[self.device]["properties"]["status"]
        is_on = bool(int(status.get(CLIMATE_POWER, 0)))

        if is_on:
            if status.get(CLIMATE_OPERATING_MODE, None) is None:
                LOGGER.error("Can not get status!")
                return HVACMode.OFF
            value = int(status.get(CLIMATE_OPERATING_MODE))
            return get_key_from_dict(CLIMATE_AVAILABLE_MODES, value)
        return HVACMode.OFF

    @property
    def hvac_modes(self) -> list:
        """Return the list of available hvac operation modes."""
        hvac_modes = [HVACMode.OFF]

        rng = 0
        for field in self.fields_range:
            if CLIMATE_OPERATING_MODE in field:
                rng = field[CLIMATE_OPERATING_MODE]
                break
        for mode, value in CLIMATE_AVAILABLE_MODES.items():
            if (value >= 0 and
                    1 << value & rng):
                hvac_modes.append(mode)

        return hvac_modes

    async def async_set_hvac_mode(self, hvac_mode) -> None:
        """Set new target hvac mode."""
        status = self.coordinator.data[self.device]["properties"]["status"]
        is_on = bool(int(status.get(CLIMATE_POWER, 0)))

        if hvac_mode == HVACMode.OFF:
            await self.client.set_device(self.device, CLIMATE_POWER, 0)
        else:
            mode = CLIMATE_AVAILABLE_MODES.get(hvac_mode)
            await self.client.set_device(self.device, CLIMATE_OPERATING_MODE, mode)
            if not is_on:
                await self.client.set_device(self.device, CLIMATE_POWER, 1)

        await asyncio.sleep(1)
        await self.coordinator.async_request_refresh()

    @property
    def preset_mode(self) -> str:
        """Return the current preset mode, e.g., home, away, temp."""
        status = self.coordinator.data[self.device]["properties"]["status"]
        is_on = bool(int(status.get(CLIMATE_POWER, 0)))
        preset_mode = PRESET_NONE

        for key, mode in CLIMATE_AVAILABLE_PRESET_MODES.items():
            if key in status and status[key]:
                preset_mode = mode
                break

        preset_mode = preset_mode if is_on else PRESET_NONE

        return preset_mode

    @property
    def preset_modes(self) -> list:
        """Return a list of available preset modes."""
        fields = self.fields
        modes = [PRESET_NONE]

        for fld in fields:
            if fld in CLIMATE_AVAILABLE_PRESET_MODES:
                modes.append(CLIMATE_AVAILABLE_PRESET_MODES[fld])

        return modes

    async def async_set_preset_mode(self, preset_mode) -> None:
        """Set new preset mode."""
        info = await self.client.get_device_with_info(self.device)
        is_on = bool(int(info["status"].get(CLIMATE_POWER, 0)))

        func = get_key_from_dict(CLIMATE_AVAILABLE_PRESET_MODES, preset_mode)

        await self.client.set_device(self.device, func, 1)
        if not is_on:
            await self.client.set_device(self.device, CLIMATE_POWER, 1)

        await self.coordinator.async_request_refresh()

    @property
    def fan_mode(self) -> str:
        """Return the fan setting."""
        status = self.coordinator.data[self.device]["properties"]["status"]
        fan_mode = int(status.get(CLIMATE_FAN_SPEED, 0))
        value = get_key_from_dict(CLIMATE_AVAILABLE_FAN_MODES, fan_mode)
        return value

    @property
    def fan_modes(self) -> list:
        """Return the list of available fan modes."""
        #return ["Auto", "1", "2", "3"]
        modes = []

        rng = 0
        for field in self.fields_range:
            if CLIMATE_FAN_SPEED in field:
                rng = field[CLIMATE_FAN_SPEED]
                break

        for mode, value in CLIMATE_AVAILABLE_FAN_MODES.items():
            if ((value >= 1) and (rng >= (1 << (value - 1)))):
                modes.append(mode)

        modes.append("Auto")

        return modes

    async def async_set_fan_mode(self, fan_mode) -> None:
        """Set new fan mode."""

        value = CLIMATE_AVAILABLE_FAN_MODES[fan_mode]
        await self.client.set_device(self.device, CLIMATE_FAN_SPEED, value)
        await self.coordinator.async_request_refresh()

    @property
    def swing_mode(self) -> str:
        """Return the swing setting."""
        status = self.coordinator.data[self.device]["properties"]["status"]
        swing_vertical = status.get(CLIMATE_SWING_VERTICAL, 0)
        swing_horizontal = status.get(CLIMATE_SWING_HORIZONTAL, 0)
        swing_vertical_level = status.get(CLIMATE_SWING_VERTICAL_LEVEL, 0)
        swing_horizontal_level = status.get(CLIMATE_SWING_HORIZONTAL_LEVEL, 0)
        mode = SWING_OFF

        if ((swing_vertical or swing_vertical_level) and (swing_horizontal or swing_horizontal_level)):
            mode = SWING_BOTH

        if ((swing_vertical or swing_vertical_level) or (swing_horizontal or swing_horizontal_level)):
            mode = SWING_ON

        if (swing_vertical or swing_vertical_level):
            mode = SWING_VERTICAL

        if (swing_horizontal or swing_horizontal_level):
            mode = SWING_HORIZONTAL

        self._swing_mode = mode
        self._swing_vertical_level = swing_vertical_level
        self._swing_horizontal_level = swing_horizontal_level
        return mode

    @property
    def swing_modes(self) -> list:
        """Return the list of available swing modes.

        Requires ClimateEntityFeature.SWING_MODE.
        """
        status = self.status
        swing_modes = [SWING_ON, SWING_OFF]

        swing_vertical = status.get(CLIMATE_SWING_VERTICAL, None)
        if swing_vertical is not None:
            swing_modes.append(SWING_VERTICAL)

        swing_horizontal = status.get(CLIMATE_SWING_HORIZONTAL, None)
        if swing_horizontal is not None:
            swing_modes.append(SWING_HORIZONTAL)

        if swing_vertical is not None and swing_horizontal  is not None:
            swing_modes.append(SWING_BOTH)

        return swing_modes

    async def async_set_swing_mode(self, swing_mode) -> None:
        """Set new target swing operation."""
        status = self.coordinator.data[self.device]["properties"]["status"]
        swing_vertical = status.get(CLIMATE_SWING_VERTICAL, None)
        swing_horizontal = status.get(CLIMATE_SWING_HORIZONTAL, None)
        swing_vertical_level = status.get(CLIMATE_SWING_VERTICAL_LEVEL, None)
        swing_horizontal_level = status.get(CLIMATE_SWING_HORIZONTAL_LEVEL, None)

        if swing_mode == SWING_ON:
            if self._swing_mode == SWING_HORIZONTAL:
                if swing_horizontal:
                    await self.client.set_device(self.device, CLIMATE_SWING_HORIZONTAL, 1)
                if swing_horizontal_level:
                    await self.client.set_device(self.device, CLIMATE_SWING_HORIZONTAL_LEVEL, self._swing_horizontal_level)
            if self._swing_mode == SWING_VERTICAL:
                if swing_vertical:
                    await self.client.set_device(self.device, CLIMATE_SWING_VERTICAL, 1)
                if swing_vertical_level:
                    await self.client.set_device(self.device, CLIMATE_SWING_VERTICAL_LEVEL, self._swing_vertical_level)

        if swing_mode == SWING_OFF:
            if swing_horizontal:
                await self.client.set_device(self.device, CLIMATE_SWING_HORIZONTAL, 0)
            if swing_horizontal_level:
                await self.client.set_device(self.device, CLIMATE_SWING_HORIZONTAL_LEVEL, 0)
            if swing_vertical:
                await self.client.set_device(self.device, CLIMATE_SWING_VERTICAL, 0)
            if swing_vertical_level:
                await self.client.set_device(self.device, CLIMATE_SWING_VERTICAL_LEVEL, 0)

        if swing_mode == SWING_HORIZONTAL:
            if swing_horizontal:
                await self.client.set_device(self.device, CLIMATE_SWING_HORIZONTAL, 1)
            if swing_horizontal_level:
                await self.client.set_device(self.device, CLIMATE_SWING_HORIZONTAL_LEVEL, self._swing_horizontal_level)
        if swing_mode == SWING_VERTICAL:
            if swing_vertical:
                await self.client.set_device(self.device, CLIMATE_SWING_VERTICAL, 1)
            if swing_vertical_level:
                await self.client.set_device(self.device, CLIMATE_SWING_VERTICAL_LEVEL, self._swing_vertical_level)

        if swing_mode == SWING_BOTH:
            if swing_horizontal:
                await self.client.set_device(self.device, CLIMATE_SWING_HORIZONTAL, 1)
            if swing_horizontal_level:
                await self.client.set_device(self.device, CLIMATE_SWING_HORIZONTAL_LEVEL, self._swing_horizontal_level)
            if swing_vertical:
                await self.client.set_device(self.device, CLIMATE_SWING_VERTICAL, 1)
            if swing_vertical_level:
                await self.client.set_device(self.device, CLIMATE_SWING_VERTICAL_LEVEL, self._swing_vertical_level)

        await self.coordinator.async_request_refresh()

    @property
    def target_temperature(self) -> int:
        """Return the temperature we try to reach."""
        status = self.coordinator.data[self.device]["properties"]["status"]
        temp = float(status.get(CLIMATE_TARGET_TEMPERATURE, 0))
        return temp

    async def async_set_temperature(self, **kwargs):
        """ Set new target temperature """
        temp = kwargs.get(ATTR_TEMPERATURE)
        await self.client.set_device(self.device, CLIMATE_TARGET_TEMPERATURE, int(temp))
        await self.coordinator.async_request_refresh()

    @property
    def current_temperature(self) -> int:
        """Return the current temperature."""
        status = self.coordinator.data[self.device]["properties"]["status"]
        temp = float(status.get(CLIMATE_TEMPERATURE_INDOOR, 0))
        return temp

    @property
    def min_temp(self) -> int:
        """ Return the minimum temperature """
        mini_temp = CLIMATE_MINIMUM_TEMPERATURE
        return mini_temp
        rng = 0
        for field in self.fields_range:
            if CLIMATE_TARGET_TEMPERATURE in field:
                rng = field[CLIMATE_TARGET_TEMPERATURE]
                break
        mini_temp = rng - int(rng / 100) * 100

        return mini_temp

    @property
    def max_temp(self) -> int:
        """ Return the maximum temperature """
        max_temp = CLIMATE_MAXIMUM_TEMPERATURE
        return max_temp
        rng = 0
        for field in self.fields_range:
            if CLIMATE_TARGET_TEMPERATURE in field:
                rng = field[CLIMATE_TARGET_TEMPERATURE]
                break
        max_temp = int(rng / 100)

        return max_temp

    @property
    def target_temperature_step(self) -> float:
        """ Return temperature step """
        return CLIMATE_TEMPERATURE_STEP
