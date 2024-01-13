from secrets import UNIQE_ID_PRE

LED_ENABLE = True
LED_PIN = "LED"

# Out Pins
ST_UP_PIN = 4
ST_DN_PIN = 5
ST_CL_PIN = 9
ST_ON_PIN = 10

# In Pins
ST_UP_C_PIN = 14
ST_DN_C_PIN = 15
ST_CL_C_PIN = 19
ST_ON_C_PIN = 20

DEB_TIME = 500

MIN_TEMP = 170
MAX_TMP = 500
START_TMP = 350
TMP_STEP = 5


DIR_DWN = "D"
DIR_UP = "U"

BTN_DELAY = 100

AV_MSG = "online"
AV_PERIOD = 15000


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
    "temp_stat_t": "~/status/temp",
    "temp_cmd_t": "~/command/temp",
    "avty_t": "~/status/availability",
    "modes": AV_MODES,
    "dev": CFG_DEV,
}


MD_CMD_TPC = CMD_TPC + "/mode"
TMP_CMD_TPC = CMD_TPC + "/temp"

MD_ST_TPC = ST_TPC + "/mode"
TMP_ST_TPC = ST_TPC + "/temp"
