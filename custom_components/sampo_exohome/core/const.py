"""Define constants for the Sampo Smart Home integration."""

from logging import getLogger

LOGGER = getLogger(__package__)


DEVICE_TYPE_CLIMATE = 1
DEVICE_TYPE_WASHING_MACHINE = 3
DEVICE_TYPE_DEHUMIDIFIER = 4
DEVICE_TYPE_AIRPURIFIER = 8
DEVICE_TYPE_FAN = 15

FIELDS_RANGE = "fields_range"

CLIMATE_AVAILABLE_FAN_MODES = {
    "Auto": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "11": 11,
    "12": 12,
    "13": 13,
    "14": 14,
    "15": 15
}
CLIMATE_MINIMUM_TEMPERATURE = 16
CLIMATE_MAXIMUM_TEMPERATURE = 30
CLIMATE_TEMPERATURE_STEP = 1.0
CLIMATE_ON_TIMER_MIN = 0
CLIMATE_ON_TIMER_MAX = 1440
CLIMATE_OFF_TIMER_MIN = 0
CLIMATE_OFF_TIMER_MAX = 1440

CLIMATE_POWER = "H00"
CLIMATE_OPERATING_MODE = "H01"
CLIMATE_FAN_SPEED = "H02"
CLIMATE_TARGET_TEMPERATURE = "H03"
CLIMATE_TEMPERATURE_INDOOR = "H04"
CLIMATE_SLEEP_MODE = "H05"
CLIMATE_FUZZY_MODE = "H07"
CLIMATE_PICOPURE_MODE = "H08"
CLIMATE_TIMER_ON = "H0B"
CLIMATE_TIMER_OFF = "H0C"
CLIMATE_SWING_VERTICAL = "H0E"
CLIMATE_SWING_VERTICAL_LEVEL = "H0F"
CLIMATE_SWING_HORIZONTAL = "H10"
CLIMATE_SWING_HORIZONTAL_LEVEL = "H11"
CLIMATE_SET_HUMIDITY = "H13"
CLIMATE_HUMIDITY_INDOOR = "H14"
CLIMATE_ERROR_CODE = "H15"
CLIMATE_ANTI_MILDEW = "H17"
CLIMATE_AUTO_CLEAN = "H18"
CLIMATE_ACTIVITY = "H19"
CLIMATE_BOOST = "H1A"
CLIMATE_ECO = "H1B"
CLIMATE_LIMITED_POWER = "H1C"
CLIMATE_CONTROLLER_MODE = "H1D"
CLIMATE_BUZZER = "H1E"
CLIMATE_TEMPERATURE_OUTDOOR = "H21"
CLIMATE_OPERATING_CURRENT = "H24"
CLIMATE_OPERATING_POWER = "H27"
CLIMATE_ENERGY = "H28"
CLIMATE_RESERVED = "H7F"

FAN_POWER = "H00"
FAN_OPERATING_MODE = "H01"
FAN_SPEED = "H02"
FAN_TEMPERATURE_INDOOR = "H03"
FAN_OSCILLATE = "H05"

FAN_PRESET_MODES = {
    "mode 1": 0,
    "mode 2": 1,
    "mode 3": 2,
    "mode 4": 3,
    "mode 5": 4
}

AIRPURIFIER_OPERATING_MODE = "H01"
AIRPURIFIER_AIR_QUALITY = "H04"
AIRPURIFIER_RESET_FILTER_NOTIFY = "H05"
AIRPURIFIER_PICOPURE = "H07"
AIRPURIFIER_BUZZER = "H08"
AIRPURIFIER_UNKNOWN1 = "H60"
AIRPURIFIER_PM25 = "H61"
AIRPURIFIER_LIGHT = "H62"
AIRPURIFIER_RUNNING_TIME = "H63"
AIRPURIFIER_UNKNOWN2 = "H64"
AIRPURIFIER_RESERVED = "H7F"

AIRPURIFIER_PICOPURE_PRESET = "Picopure"
AIRPURIFIER_PRESET_MODES = {
    AIRPURIFIER_PICOPURE: AIRPURIFIER_PICOPURE_PRESET,
}
