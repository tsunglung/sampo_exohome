"""Support for Exohome sensors."""

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    UnitOfElectricCurrent,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .core.const import (
    DEVICE_TYPE_AIRPURIFIER,
    DEVICE_TYPE_CLIMATE,
    AIRPURIFIER_AIR_QUALITY,
    AIRPURIFIER_PM25,
    AIRPURIFIER_RUNNING_TIME,
    CLIMATE_TEMPERATURE_INDOOR,
    CLIMATE_ERROR_CODE,
    CLIMATE_TEMPERATURE_OUTDOOR,
    CLIMATE_OPERATING_CURRENT,
    CLIMATE_OPERATING_POWER,
    CLIMATE_ENERGY
)
from .coordinator import ExohomeDataUpdateCoordinator
from .entity import ExohomeEntity, ExohomeEntityDescription
from .const import (
    DOMAIN,
    LOGGER
)


@dataclass(frozen=True, kw_only=True)
class ExohomeSensorDescription(SensorEntityDescription, ExohomeEntityDescription):
    """Describe a Exohome sensor."""


AIRPURIFIER_SENSORS: tuple[ExohomeSensorDescription, ...] = (
    ExohomeSensorDescription(
        key=AIRPURIFIER_AIR_QUALITY,
        name="Air Quality",
        device_class= SensorDeviceClass.AQI,
        icon='mdi:leaf'
    ),
    ExohomeSensorDescription(
        key=AIRPURIFIER_PM25,
        name="PM2.5",
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PM25,
        icon="mdi:chemical-weapon"
    ),
    ExohomeSensorDescription(
        key=AIRPURIFIER_RUNNING_TIME,
        name="Running Time",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTime.MINUTES,
        icon="mdi:clock-outline"
    )
)

CLIMATE_SENSORS: tuple[ExohomeSensorDescription, ...] = (
    ExohomeSensorDescription(
        key=CLIMATE_TEMPERATURE_INDOOR,
        name="Inside temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        icon="mdi:thermometer"
    ),
    ExohomeSensorDescription(
        key=CLIMATE_ERROR_CODE,
        name="Error Code",
        icon="mdi:alert-circle"
    ),
    ExohomeSensorDescription(
        key=CLIMATE_TEMPERATURE_OUTDOOR,
        name="Outside temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.TEMPERATURE,
        icon="mdi:thermometer"
    ),
    ExohomeSensorDescription(
        key=CLIMATE_OPERATING_CURRENT,
        name="Operation Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.CURRENT,
        icon="mdi:current-ac"
    ),
    ExohomeSensorDescription(
        key=CLIMATE_OPERATING_POWER,
        name="Operation Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.POWER,
        icon="mdi:flash"
    ),
    ExohomeSensorDescription(
        key=CLIMATE_ENERGY,
        name="Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        device_class=SensorDeviceClass.ENERGY,
        icon="mdi:flash"
    ),
)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Exohome sensors based on a config entry."""
    coordinator: ExohomeDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    devices = coordinator.data

    if ((isinstance(devices, dict) and len(devices) <= 1) or (devices is None)):
        return

    try:
        entities = []

        for device, info in devices.items():
            properties = info.get("properties", None)
            if properties:
                device_id = int(properties["profile"]["esh"]["device_id"])
                fields = properties.get("fields", [])
                if device_id == DEVICE_TYPE_AIRPURIFIER:
                    for description in AIRPURIFIER_SENSORS:
                        if description.key in fields:
                            entities.extend(
                                [ExohomeSensor(
                                    coordinator, device, info, description)]
                            )

                if device_id == DEVICE_TYPE_CLIMATE:
                    for description in CLIMATE_SENSORS:
                        if description.key in fields:
                            entities.extend(
                                [ExohomeSensor(
                                    coordinator, device, info, description)]
                            )

        async_add_entities(entities)
    except AttributeError as ex:
        LOGGER.error(ex)

    return True


class ExohomeSensor(ExohomeEntity, SensorEntity):
    """Define a Exohome sensor."""
    entity_description: ExohomeSensorDescription

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
        """Return the name of the sensor."""
        return f"{self.entity_description.name}"

    @property
    def unique_id(self):
        """Return the unique of the sensor."""
        return f"{self.device}_{self._device_id}_{self.entity_description.key}"

    @property
    def native_value(self) -> float | str | None:
        """Return the value reported by the sensor."""
        status = self.coordinator.data[self.device]["properties"]["status"]
        if self.entity_description.key in [CLIMATE_ENERGY, CLIMATE_OPERATING_CURRENT]:
            return float(int(status[self.entity_description.key]) * 0.1)
        return status[self.entity_description.key]
