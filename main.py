from lib.mqtt_as import MQTTClient, config
import asyncio
import json
import time
import machine

from machine import Timer, Pin

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
    BTN_DELAY
)

from constants import (
    ST_ON_PIN,
    ST_CL_PIN,
    ST_UP_PIN,
    ST_DN_PIN,
    ST_ON_C_PIN,
    ST_CL_C_PIN,
    ST_DN_C_PIN,
    ST_UP_C_PIN,
)

# Local configuration
config["ssid"] = WIFI_AP
config["wifi_pw"] = WIFI_PWD
config["server"] = MQTT_HOST

cur_mode = MODE_OFF
cur_temp = START_TMP
debounce_time = 0

oven_on = Pin(ST_ON_PIN, Pin.OUT, Pin.PULL_DOWN)
oven_clear_off = Pin(ST_CL_PIN, Pin.OUT, Pin.PULL_DOWN)
oven_temp_up = Pin(ST_UP_PIN, Pin.OUT, Pin.PULL_DOWN)
oven_temp_down = Pin(ST_DN_PIN, Pin.OUT, Pin.PULL_DOWN)

async def wait_pin_change(pin):
    # wait for pin to change value
    # it needs to be stable for a continuous 20ms
    cur_value = pin.value()
    active = 0
    while active < DEB_TIME:
        if pin.value() != cur_value:
            active += 1
        else:
            active = 0
        await asyncio.sleep_ms(1)

async def set_off():
    oven_clear_off.off()
    oven_clear_off.on()
    await asyncio.sleep_ms(BTN_DELAY)
    oven_clear_off.off()

async def set_on():
    oven_on.off()
    oven_on.on()
    await asyncio.sleep_ms(BTN_DELAY)
    oven_on.off()


async def set_temp(set_point):
    global cur_mode
    direction = None

    if set_point > MAX_TMP:
        set_point = MAX_TMP

    if set_point < MIN_TEMP:
        set_point = MIN_TEMP

    if set_point == START_TMP:
        pass
    elif set_point < START_TMP:
        steps = int((START_TMP - set_point) / TMP_STEP)
        direction = DIR_DWN
    elif set_point > START_TMP:
        steps = int((set_point - START_TMP) / TMP_STEP)
        direction = DIR_UP

    if cur_mode == MODE_OFF:
        await set_on()

    for i in range(steps):
        if direction == DIR_UP:
            oven_temp_up.on()
            await asyncio.sleep_ms(BTN_DELAY)
            oven_temp_up.off()
        if direction == DIR_DWN:
            oven_temp_down.on()
            await asyncio.sleep_ms(BTN_DELAY)
            oven_temp_down.off()

    if cur_mode == MODE_OFF:
        await set_on()
        cur_mode = MODE_HEAT

async def received_command(command, mtch_topic, client):
    global cur_mode
    global cur_temp

    if mtch_topic == TMP_CMD_TPC:
        print("Set Temp to %s" % command)
        new_temp = int(float(command))
        if MIN_TEMP < new_temp < MAX_TMP:
            cur_temp = new_temp
            await set_temp(cur_temp)
            await update_temp_state(client)
            await update_mode_state(client)
            print("Set Temp to %s" % cur_temp)
    elif mtch_topic == MD_CMD_TPC:
        if command in AV_MODES and command != cur_mode:
            cur_mode = command
            if cur_mode == MODE_OFF:
                await set_off()
            if cur_mode == MODE_HEAT:
                await set_on()
                cur_temp = START_TMP
                await update_temp_state(client)
            await update_mode_state(client)
            print("Set Mode to %s" % cur_mode)


async def update_temp_state(client):
    await client.publish(TMP_ST_TPC.encode("utf_8"), str(cur_temp).encode("utf_8"))


async def update_mode_state(client):
    await client.publish(MD_ST_TPC.encode("utf_8"), cur_mode.encode("utf_8"))


async def send_config(client):  # Send Config Message
    config_topic = f"{MQTT_PREFIX}/climate/{ID}/config"
    await client.publish(
        config_topic, json.dumps(CFG_MSG).encode("utf_8"), qos=1, retain=True
    )


async def read_on_button(client):
    global cur_mode
    oven_on_ctl = Pin(ST_ON_C_PIN, Pin.IN, Pin.PULL_UP)
    while True:
        await wait_pin_change(oven_on_ctl)
        cur_mode = MODE_HEAT
        await update_mode_state(client)


async def read_clr_button(client):
    global cur_mode
    global cur_temp
    oven_clear_off_ctl = Pin(ST_CL_C_PIN, Pin.IN, Pin.PULL_UP)
    while True:
        await wait_pin_change(oven_clear_off_ctl)
        cur_temp = START_TMP
        cur_mode = MODE_OFF
        await update_temp_state(client)
        await update_mode_state(client)


async def read_up_button(client):
    global cur_temp
    oven_temp_up_ctl = Pin(ST_UP_C_PIN, Pin.IN, Pin.PULL_UP)
    while True:
        await wait_pin_change(oven_temp_up_ctl)
        if cur_temp < MAX_TMP:
            cur_temp += TMP_STEP
            await update_temp_state(client)


async def read_dwn_button(client):
    global cur_temp
    oven_temp_down_ctl = Pin(ST_DN_C_PIN, Pin.IN, Pin.PULL_UP)
    while True:
        await wait_pin_change(oven_temp_down_ctl)
        if cur_temp > MIN_TEMP:
            cur_temp -= TMP_STEP
            await update_temp_state(client)


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
        await send_config(client)
        await update_mode_state(client)
        await update_temp_state(client)
        asyncio.create_task(read_up_button(client))
        asyncio.create_task(read_dwn_button(client))
        asyncio.create_task(read_on_button(client))
        asyncio.create_task(read_clr_button(client))


async def main(client):
    await client.connect()
    for coroutine in (
        up,
        messages,
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
finally:
    client.close()  # Prevent LmacRxBlk:1 errors
