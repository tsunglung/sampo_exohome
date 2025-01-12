"""Define constants for the Sampo Smart Home integration."""

from logging import getLogger
from datetime import timedelta

from homeassistant.components.climate.const import (
    HVACMode,
    PRESET_BOOST,
    PRESET_ECO,
    PRESET_COMFORT,
    PRESET_ACTIVITY,
    PRESET_SLEEP
)

from .core.const import (
    CLIMATE_ACTIVITY,
    CLIMATE_BOOST,
    CLIMATE_ECO,
    CLIMATE_PICOPURE_MODE,
    CLIMATE_SLEEP_MODE
)

DOMAIN = "sampo_exohome"
LOGGER = getLogger(__package__)

REFRESH_TOKEN_EXPIRY_TIME = timedelta(days=30)

CONF_REFRESH_TOKEN = "refresh_token"
CONF_USER_ID = "user_id"
CONF_TOKEN_EXPIRES_IN = "token_expires_in"

SENSOR_BATTERY = "low_battery"
SENSOR_DOOR = "door"
SENSOR_GARAGE_DOOR = "garage_door"
SENSOR_LEAK = "leak"
SENSOR_MISSING = "missing"
SENSOR_MOLD = "mold"
SENSOR_SAFE = "safe"
SENSOR_SLIDING = "sliding"
SENSOR_SMOKE_CO = "alarm"
SENSOR_TEMPERATURE = "temperature"
SENSOR_WINDOW_HINGED = "window_hinged"

CLIMATE_AVAILABLE_MODES = {
    HVACMode.OFF: -1,
    HVACMode.COOL: 0,
    HVACMode.DRY: 1,
    HVACMode.FAN_ONLY: 2,
    HVACMode.AUTO: 3,
    HVACMode.HEAT: 4
}

CLIMATE_AVAILABLE_PRESET_MODES = {
    CLIMATE_ACTIVITY: PRESET_ACTIVITY,
    CLIMATE_BOOST: PRESET_BOOST,
    CLIMATE_ECO: PRESET_ECO,
    CLIMATE_PICOPURE_MODE: PRESET_COMFORT,
    CLIMATE_SLEEP_MODE: PRESET_SLEEP
}
