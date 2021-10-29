from gpiozero import CPUTemperature
import RPi.GPIO as GPIO
import time
import signal
from datetime import datetime
import logging
from systemd.journal import JournaldLogHandler
import json

FAN_PORT = 17
THRESHOLD = 65  # 47
HYSTERESIS = 15
CONF_FILE = "/usr/local/etc/fan_control.json"

logger = logging.getLogger('fan')
logger.addHandler(JournaldLogHandler())
logger.setLevel(logging.INFO)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(FAN_PORT, GPIO.OUT)
GPIO.output(FAN_PORT, GPIO.LOW)


def log(msg):
    print('{}: {}'.format(datetime.now(), msg))
    logger.info(msg)


def tidyup(msg, *args):
    GPIO.output(FAN_PORT, 0)
    log("Caught terminate signal. Cleanup fan off.")
    exit(0)


if __name__ == '__main__':

    try:
        with open(CONF_FILE) as json_file:
            data = json.load(json_file)
            log("Using local configuration file: {}".format(CONF_FILE))

            FAN_PORT = int(data['fan_port'])
            THRESHOLD = int(data['threshold'])
            HYSTERESIS = int(data['hysteresis'])
    except:
        pass

    log('fan_port: {}'.format(FAN_PORT))
    log('threshold: {}'.format(THRESHOLD))
    log('hysteresis: {}'.format(HYSTERESIS))

    signal.signal(signal.SIGINT, tidyup)
    signal.signal(signal.SIGTERM, tidyup)

    log('Current temp: {}C'.format(CPUTemperature().temperature))
    while True:
        cpu = CPUTemperature()

        out = None
        if cpu.temperature >= THRESHOLD:
            out = 1
        elif cpu.temperature <= THRESHOLD - HYSTERESIS:
            out = 0

        if out != None and GPIO.input(FAN_PORT) != out:
            log('FAN {} temp: {}C'.format('ON' if out else 'OFF', cpu.temperature))
            GPIO.output(FAN_PORT, out)

        time.sleep(1.0)
