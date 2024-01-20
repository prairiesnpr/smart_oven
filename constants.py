import array
from secrets import UNIQE_ID_PRE

LED_ENABLE = True
LED_PIN = "LED"

# Out Pins (7)
# Start Top left, DN-Right-UP
ST_ON_PIN = 5  # Bake
# ST_BR_PIN = 3  # Broil
# ST_TM_PIN = 4  # Timer
# ST_CK_PIN = 5  # Clock
ST_CL_PIN = 2  # CLR/OFF
ST_DN_PIN = 3  # DWN
ST_UP_PIN = 4  # UP

# Think 2 is clear
# In Pins
# Not bothering to monitor the other inputs, just don't see a point
ST_HT_IN_PIN = 7  # Heat Mode, Bake or Broil
ST_UP_AIN_PIN = 26  # Temp Up
ST_DN_AIN_PIN = 27  # Temp Dwn

CONSIDER_OFF = 30000  # Analog pin value to consider off


# LED In Pins
ST_ON_LED_PIN = 14
ST_BL_LED_PIN = 15

# Actual Temp
ST_T_AIN_PIN = 28


DEB_TIME = 10

MIN_TEMP = 170
MAX_TMP = 500
START_TMP = 350
TMP_STEP = 5


DIR_DWN = "D"
DIR_UP = "U"

BTN_DELAY = 100  # ms

BTN_STEP_DELAY = 200  # ms
BTN_HT_DELAY = 200  # ms
BTN_CLD_DELAY = 300  # ms

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
V_IN = 3.29  # TODO: Research how the pico uses analog v_ref, seems like I shouldn't need to do this
R_TEMP = 2000
C_F_MULT = 1.8
C_F_OFFSET = 32
U16_MAX = 65535
U12_MAX = 4095

BETA = -410.51
KELVIN_C = 273.15
T_CORR = 15

A = 63.93648271e-03
B = -113.5216743e-04
C = 550.7111202e-07
# Rt = (Vout * R1) / (Vin - Vout)
# tk = 1/(A+(B*math.log(Rt))+C*math.pow(math.log(Rt),3))
# tc = tk - KELVIN_C
# tf = (tc*1.8) + 32

# Bandpass filter
# FIR_COEFF = array.array('i', (272,449,-266,-540,-55,-227,-1029,745,3927,1699,-5616,-6594,2766,9228,2766
#    ,-6594,-5616,1699,3927,745,-1029,-227,-55,-540,-266,449,272))

FIR_COEFF = array.array(
    "i",
    (
        -1432,
        0,
        1630,
        0,
        3450,
        0,
        -12571,
        0,
        17360,
        0,
        -12571,
        0,
        3450,
        0,
        1630,
        0,
        -1432,
    ),
)

FIR_SCALE = 16
