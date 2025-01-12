"""Support for Exohome select."""

from dataclasses import dataclass

from homeassistant.components.select import (
    SelectEntityDescription,
    SelectEntity
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .core.const import (
    DEVICE_TYPE_AIRPURIFIER,
    DEVICE_TYPE_CLIMATE,
    AIRPURIFIER_LIGHT,
    AIRPURIFIER_RESERVED,
    CLIMATE_FUZZY_MODE,
    CLIMATE_ACTIVITY,
    CLIMATE_SWING_VERTICAL_LEVEL,
    CLIMATE_SWING_HORIZONTAL_LEVEL
)
from .coordinator import ExohomeDataUpdateCoordinator
from .entity import ExohomeEntity, ExohomeEntityDescription
from .const import (
    DOMAIN,
    LOGGER
)


@dataclass(frozen=True, kw_only=True)
class ExohomeSelectDescription(SelectEntityDescription, ExohomeEntityDescription):
    """Describe a Exohome select."""
    options_value: list[str] | None = None


AIRPURIFIER_SELECTS: tuple[ExohomeSelectDescription, ...] = (
    ExohomeSelectDescription(
        key=AIRPURIFIER_LIGHT,
        name="Light",
        entity_category=EntityCategory.CONFIG,
        icon='mdi:brightness-5',
        options=["Light", "Dark", "Off"],
        options_value=["0", "1", "2"]
    ),
    ExohomeSelectDescription(
        key=AIRPURIFIER_RESERVED,
        name="Reserved",
        entity_category=EntityCategory.CONFIG,
        icon='mdi:help',
        options=[],
        options_value=[]
    )
)

CLIMATE_SELECTS: tuple[ExohomeSelectDescription, ...] = (
    ExohomeSelectDescription(
        key=CLIMATE_FUZZY_MODE,
        name="Fuzzy Mode",
        entity_category=EntityCategory.CONFIG,
        icon='mdi:broom',
        options=["Better", "Too cloud", "Too hot", "Off", "On"],
        options_value=["0", "1", "2", "3", "4"],
    ),
    ExohomeSelectDescription(
        key=CLIMATE_ACTIVITY,
        name="Motion Detect",
        entity_category=EntityCategory.CONFIG,
        icon='mdi:motion-sensor',
        options=["Off", "To human", "Not to human", "Auto"],
        options_value=["0", "1", "2", "3"]
    ),
    ExohomeSelectDescription(
        key=CLIMATE_SWING_VERTICAL_LEVEL,
        name="Swing Vertical Level",
        entity_category=EntityCategory.CONFIG,
        icon='mdi:fan-speed-3',
        options=["Off", "1", "2", "3"],
        options_value=["0", "1", "2", "3"]
    ),
    ExohomeSelectDescription(
        key=CLIMATE_SWING_HORIZONTAL_LEVEL,
        name="Swing Horizontal Level",
        entity_category=EntityCategory.CONFIG,
        icon='mdi:fan-speed-3',
        options=["Off", "1", "2", "3"],
        options_value=["0", "1", "2", "3"]
    )
)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Exohome selects based on a config entry."""
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
                for description in AIRPURIFIER_SELECTS:
                    if description.key in fields:
                        entities.extend(
                            [ExohomeSelect(
                                coordinator, device, info, description)]
                        )

            if device_id == DEVICE_TYPE_CLIMATE:
                for description in CLIMATE_SELECTS:
                    if description.key in fields:
                        entities.extend(
                            [ExohomeSelect(
                                coordinator, device, info, description)]
                        )

        async_add_entities(entities)
    except AttributeError as ex:
        LOGGER.error(ex)

    return True


class ExohomeSelect(ExohomeEntity, SelectEntity):
    """Define a Exohome select."""
    entity_description: ExohomeSelectDescription

    def __init__(
        self,
        coordinator,
        device,
        info,
        description
    ):
        super().__init__(coordinator, device, info)
        self.entity_description = description
        self._range = {}

    @property
    def name(self):
        """Return the name of the select."""
        return f"{self.entity_description.name}"

    @property
    def unique_id(self):
        """Return the unique of the select."""
        return f"{self.device}_{self._device_id}_{self.entity_description.key}"

    @property
    def options(self) -> list:
        """Return a set of selectable options."""
        for field in self.fields_range:
            for key, value in field.items():
                if ((self.entity_description.key == key) and (isinstance(value, int))):
                    bitpos = 0
                    while value != 0:
                        bitpos = bitpos + 1
                        value = value >> 1
                    for i in range(0, bitpos):
                        self._range[str(i)] = i
                    return list(self._range.keys())
        return self.entity_description.options

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        status = self.coordinator.data[self.device]["properties"]["status"]
        if status:
            if len(self._range) >= 1:
                return str(status[self.entity_description.key])
            else:
                value = str(status[self.entity_description.key])
                index = self.entity_description.options_value.index(value)
                return self.entity_description.options[index]
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if len(self._range) >= 1:
            value = self._range[option]
        else:
            index  = self.entity_description.options.index(option)
            value = self.entity_description.options_value[index]

        await self.client.set_device(
            self.device, self.entity_description.key, int(value))
        await self.coordinator.async_request_refresh()
