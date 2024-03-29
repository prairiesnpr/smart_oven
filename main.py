from lib.mqtt_as import MQTTClient, config
import asyncio
import json
import time
import machine
import math

from machine import Timer, Pin
from machine import ADC
from array import array
from fir import fir
from avg_pico import avg


from secrets import WIFI_AP, WIFI_PWD, MQTT_HOST

from constants import (
    SUB_TPC,
    AV_TPC,
    AV_MSG,
    CFG_MSG,
    ID,
    MQTT_PREFIX,
    TMP_ST_TPC,
    MD_ST_TPC,
    MODE_HEAT,
    MODE_OFF,
    START_TMP,
    TMP_CMD_TPC,
    MIN_TEMP,
    MAX_TMP,
    MD_CMD_TPC,
    AV_MODES,
    DEB_TIME,
    TMP_STEP,
    DIR_DWN,
    DIR_UP,
    BTN_DELAY,
    TMP_CUR_TPC,
    CUR_TMP_RD_PER,
    BTN_STEP_DELAY,
    BTN_HT_DELAY,
    BTN_CLD_DELAY,
    V_IN,
    R_TEMP,
    C_F_MULT,
    C_F_OFFSET,
    U16_MAX,
)

from constants import (
    ST_ON_PIN,
    ST_CL_PIN,
    ST_UP_PIN,
    ST_DN_PIN,
    ST_HT_IN_PIN,
    ST_T_AIN_PIN,
    ST_UP_AIN_PIN,
    ST_DN_AIN_PIN,
    CONSIDER_OFF,
)

from constants import KELVIN_C, A, B, C, T_CORR
from constants import FIR_COEFF, FIR_SCALE

# Local configuration
config["ssid"] = WIFI_AP
config["wifi_pw"] = WIFI_PWD
config["server"] = MQTT_HOST

cur_mode = MODE_OFF
cur_set_temp = START_TMP
cur_act_temp = MIN_TEMP  # Need something?
cur_act_temp_raw = 0

disable_in_btn = False


oven_on_btn = Pin(ST_ON_PIN, Pin.OUT)
oven_on_btn.off()
oven_clear_off_btn = Pin(ST_CL_PIN, Pin.OUT)
oven_clear_off_btn.off()
oven_temp_up_btn = Pin(ST_UP_PIN, Pin.OUT)  # is oven on
oven_temp_up_btn.off()
oven_temp_down_btn = Pin(ST_DN_PIN, Pin.OUT)
oven_temp_down_btn.off()


async def toggle_btn(pin):
    btn = Pin(pin, Pin.OUT)
    btn.on()
    await asyncio.sleep_ms(BTN_DELAY)
    btn.off()
    await asyncio.sleep_ms(BTN_DELAY)


async def wait_pin_change(pin):
    cur_value = pin.value()
    active = 0
    while active < DEB_TIME:
        if pin.value() != cur_value:
            active += 1
        else:
            active = 0
        await asyncio.sleep_ms(1)


async def wait_analog_pin_change(pin):
    active = 0
    while active < DEB_TIME:
        if pin.read_u16() > CONSIDER_OFF:
            active += 1
        else:
            active = 0
        await asyncio.sleep_ms(1)


async def set_on(complete=False):
    await toggle_btn(ST_ON_PIN)
    await temp_up()
    if complete:
        await toggle_btn(ST_ON_PIN)


async def set_off():
    await toggle_btn(ST_CL_PIN)


async def temp_press_up():
    await toggle_btn(ST_UP_PIN)


async def temp_press_dn():
    await toggle_btn(ST_DN_PIN)


async def apply_temp(btn=None, steps=0, delay_req=False):
    btn.on()
    oven_delay = steps * BTN_STEP_DELAY
    if delay_req:
        oven_delay += BTN_CLD_DELAY
    else:
        oven_delay += BTN_HT_DELAY
    await asyncio.sleep_ms(oven_delay)
    btn.off()


async def temp_up(steps=0, delay_req=False):
    btn = Pin(ST_UP_PIN, Pin.OUT)
    await apply_temp(btn=btn, steps=steps, delay_req=delay_req)


async def temp_dn(steps=0, delay_req=False):
    btn = Pin(ST_DN_PIN, Pin.OUT)
    await apply_temp(btn=btn, steps=steps, delay_req=delay_req)


async def set_temp_long_press(set_point):
    global cur_mode
    global cur_set_temp
    global disable_in_btn

    steps = 0
    direction = None
    disable_in_btn = True

    print(f"Cur Mode: {cur_mode}, Cur Set Pnt: {cur_set_temp} Set to: {set_point}")

    if set_point > MAX_TMP:
        set_point = MAX_TMP

    if set_point < MIN_TEMP:
        set_point = MIN_TEMP

    if set_point < cur_set_temp:
        steps = abs(int((cur_set_temp - set_point) / TMP_STEP))
        direction = DIR_DWN
        print("Dir Dwn: %s Steps" % steps)

    if set_point > cur_set_temp:
        steps = abs(int((set_point - cur_set_temp) / TMP_STEP))
        direction = DIR_UP
        print("Dir Up: %s Steps" % steps)

    delay_req = False

    if cur_mode == MODE_OFF:
        await set_on(complete=False)
        delay_req = True

    if direction == DIR_UP:
        await temp_up(steps=steps, delay_req=delay_req)

    if direction == DIR_DWN:
        await temp_dn(steps=steps, delay_req=delay_req)

    if cur_mode == MODE_OFF:
        await set_on(complete=False)

    cur_set_temp = set_point
    disable_in_btn = False


async def received_command(command, mtch_topic, client):
    global cur_mode
    global cur_set_temp

    if mtch_topic == TMP_CMD_TPC:
        print("Set Temp to %s" % command)
        new_temp = int(float(command))
        if MIN_TEMP <= new_temp <= MAX_TMP:
            print("Setting Temp to %s" % new_temp)
            await set_temp_long_press(new_temp)
            await update_temp_set_state(client)
            await update_mode_state(client)
        else:
            await update_temp_set_state(client)
    elif mtch_topic == MD_CMD_TPC:
        if command in AV_MODES and command != cur_mode:
            if command == MODE_OFF:
                await set_off()
                cur_set_temp = START_TMP
            if command == MODE_HEAT:
                await set_on(complete=True)
                cur_set_temp = START_TMP
            await update_temp_set_state(client)
            await update_mode_state(client)


async def update_temp_cur_state(client):
    await client.publish(TMP_CUR_TPC.encode("utf_8"), str(cur_act_temp).encode("utf_8"))


async def update_temp_set_state(client):
    await client.publish(TMP_ST_TPC.encode("utf_8"), str(cur_set_temp).encode("utf_8"))


async def update_mode_state(client):
    await client.publish(MD_ST_TPC.encode("utf_8"), cur_mode.encode("utf_8"))


async def send_config(client):  # Send Config Message
    config_topic = f"{MQTT_PREFIX}/climate/{ID}/config"
    await client.publish(
        config_topic, json.dumps(CFG_MSG).encode("utf_8"), qos=1, retain=True
    )


async def read_heat_mode(client):
    global cur_mode
    global cur_set_temp
    oven_on = Pin(ST_HT_IN_PIN, Pin.IN, Pin.PULL_UP)
    while True:
        if not oven_on.value():
            cur_mode = MODE_HEAT
        else:
            cur_mode = MODE_OFF
        await update_mode_state(client)
        print("Wait for BK/BR pin")
        await wait_pin_change(oven_on)
        cur_set_temp = START_TMP
        if not oven_on.value():
            cur_mode = MODE_HEAT
        else:
            cur_mode = MODE_OFF
        print("Pin BK/BR")
        await update_mode_state(client)
        await update_temp_set_state(client)


# async def read_clr_button(client):
#     global cur_mode
#     global cur_set_temp
#     oven_clear_off_ctl = Pin(ST_CL_C_PIN, Pin.IN, Pin.PULL_UP)
#     while True:
#         print("Wait for CLR pin")
#         await wait_pin_change(oven_clear_off_ctl)
#         print("Pin CLR")
#         cur_set_temp = START_TMP
#         cur_mode = MODE_OFF
#         await update_temp_set_state(client)
#         await update_mode_state(client)


async def read_up_button(client):
    global cur_set_temp
    oven_temp_up_ctl = ADC(ST_UP_AIN_PIN)
    while True:
        print("Wait for UP pin")
        await wait_analog_pin_change(oven_temp_up_ctl)
        print("Pin UP")
        if cur_set_temp < MAX_TMP and not disable_in_btn:
            cur_set_temp += TMP_STEP
            await update_temp_set_state(client)


async def read_dwn_button(client):
    global cur_set_temp
    oven_temp_down_ctl = ADC(ST_DN_AIN_PIN)
    while True:
        print("Wait for DWN pin")
        await wait_analog_pin_change(oven_temp_down_ctl)
        print("Pin DWN")
        if cur_set_temp > MIN_TEMP and not disable_in_btn:
            cur_set_temp -= TMP_STEP
            await update_temp_set_state(client)


async def read_cur_tmp(client):
    global cur_act_temp_raw
    oven_current_act_temp = ADC(ST_T_AIN_PIN)
    data = array("i", (0 for _ in range(19)))  # Average over 16 samples
    data[0] = len(data)

    print("Starting temp read loop")
    while True:
        raw = oven_current_act_temp.read_u16()
        cur_act_temp_raw = avg(data, raw, 4)
        await asyncio.sleep_ms(5)


async def update_cur_temp(client):
    global cur_act_temp
    print("Starting temp loop")
    while True:
        if cur_act_temp_raw > 0:
            temp_volts = (cur_act_temp_raw * V_IN) / U16_MAX
            temp_r = (temp_volts * R_TEMP) / (V_IN - temp_volts)
            tk = 1 / (A + (B * math.log(temp_r)) + C * math.pow(math.log(temp_r), 3))
            cur_act_temp = ((tk - KELVIN_C) * C_F_MULT) + C_F_OFFSET + T_CORR
            await update_temp_cur_state(client)
        await asyncio.sleep_ms(CUR_TMP_RD_PER)


async def messages(client):  # Respond to incoming messages
    async for topic, msg, retained in client.queue:
        dec_topic = topic.decode("utf_8")
        if dec_topic in [MD_CMD_TPC, TMP_CMD_TPC]:
            await received_command(msg.decode("utf_8"), dec_topic, client)
        else:
            print((topic, msg, retained))


async def up(client):  # Respond to connectivity being (re)established
    while True:
        await client.up.wait()  # Wait on an Event
        client.up.clear()
        await client.subscribe(SUB_TPC, 1)  # renew subscriptions
        await send_config(client)  # Send the discovery msg
        await update_mode_state(client)  # Send the current mode
        await update_temp_set_state(client)  # Send the current temp

        # TODO: Will there be any issues here, do we need to cancel existing and restart them?
        # Moved to the main function, for now, still not certain where it should be
        # asyncio.create_task(read_up_button(client))
        # asyncio.create_task(read_dwn_button(client))
        # asyncio.create_task(read_on_button(client))
        # asyncio.create_task(read_clr_button(client))
        # asyncio.create_task(read_cur_tmp(client))


async def main(client):
    await client.connect()
    for coroutine in (
        up,
        messages,
        read_heat_mode,
        update_cur_temp,
        read_cur_tmp,
        # TODO: figure out a way to read temp buttons
        # read_dwn_button,
        # read_up_button,
    ):
        asyncio.create_task(coroutine(client))
    while True:
        await asyncio.sleep(5)
        # If WiFi is down the following will pause for the duration.
        await client.publish(AV_TPC, AV_MSG.encode("utf_8"), qos=1)


config["queue_len"] = 1  # Use event interface with default queue size
MQTTClient.DEBUG = True  # Optional: print diagnostic messages

try:
    client = MQTTClient(config)
except OSError:
    machine.reset()
try:
    asyncio.run(main(client))
except OSError:
    machine.reset()
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
