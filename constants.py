from secrets import UNIQE_ID_PRE

LED_ENABLE = True
LED_PIN = "LED"

# Out Pins (7)
# Start Top left, DN-Right-UP
ST_ON_PIN = 5  # Bake
#ST_BR_PIN = 3  # Broil
#ST_TM_PIN = 4  # Timer
#ST_CK_PIN = 5  # Clock
ST_CL_PIN = 2  # CLR/OFF
ST_DN_PIN = 3  # DWN
ST_UP_PIN = 4  # UP

# Think 2 is clear
# In Pins
# Not bothering to monitor the other inputs, just don't see a point
ST_UP_C_PIN = 9  # Temp Up
ST_DN_C_PIN = 10  # Temp Dwn
ST_CL_C_PIN = 11  # Clr/Off
ST_ON_C_PIN = 12  # Bake
ST_BR_C_PIN = 13  # Broil

# LED In Pins
ST_ON_LED_PIN = 14
ST_BL_LED_PIN = 15

# Actual Temp, haven't even looked at it.
ST_T_IN_PIN = 27


DEB_TIME = 10

MIN_TEMP = 170
MAX_TMP = 500
START_TMP = 350
TMP_STEP = 5


DIR_DWN = "D"
DIR_UP = "U"

BTN_DELAY = 100  # ms

CUR_TMP_RD_PER = 5000

AV_MSG = "online"
AV_PERIOD = 15000  # ms


MQTT_PREFIX = "isilentllc"
MQTT_STATUS = "status"
MQTT_CLIENT = "smartoven"

DEV_TYPE = "climate"

MODE_OFF = "off"
MODE_HEAT = "heat"
AV_MODES = [MODE_OFF, MODE_HEAT]

VER = 1
MDL = "Savvy Tech Oven Value Enhancer (STOVE)"
MNF = "iSilent LLC"
AREA = "Kitchen"
DEV = "iSilentLLC_STOVE"
NAME = f"{MNF} {MDL}"
TMP_UNT = "F"
TMP_P = 1.0
ID = f"{DEV}_{UNIQE_ID_PRE}"

CFG_DEV = {
    "sw": VER,
    "mdl": MDL,
    "mf": MNF,
    "sa": AREA,
    "name": NAME,
    "ids": [ID],
}

SUB_TPC = f"{ID}/command/+"
ST_TPC = f"{ID}/status"
CMD_TPC = f"{ID}/command"
AV_TPC = ST_TPC + "/availability"

CFG_MSG = {
    "~": ID,
    "uniq_id": ID,
    "ic": "mdi:stove",
    "max_temp": MAX_TMP,
    "min_temp": MIN_TEMP,
    "temp_unit": TMP_UNT,
    "temp_step": TMP_STEP,
    "initial": START_TMP,
    "precision": TMP_P,
    "mode_stat_t": "~/status/mode",
    "mode_cmd_t": "~/command/mode",
    "temp_stat_t": "~/status/set_temp",
    "temp_cmd_t": "~/command/set_temp",
    "curr_temp_t": "~/status/cur_temp",
    "avty_t": "~/status/availability",
    "modes": AV_MODES,
    "dev": CFG_DEV,
}


MD_CMD_TPC = CMD_TPC + "/mode"
TMP_CMD_TPC = CMD_TPC + "/set_temp"

MD_ST_TPC = ST_TPC + "/mode"
TMP_ST_TPC = ST_TPC + "/set_temp"
TMP_CUR_TPC = ST_TPC + "/cur_temp"


# Temp sensor
BETA = 3950  # Verify
KELVIN_C = 273.15  # Verify
