import threading
import time
import logging
import RPi.GPIO as GPIO
from gpiozero import CPUTemperature
from datetime import datetime
from fan_control_base import FanControlBase

logger = logging.getLogger('fan')

def log(msg):
    print('{}: {}'.format(datetime.now(), msg))
    logger.info(msg)

class FanControlThreshold(FanControlBase):
    def __init__(self, config_data):

        FAN_PORT = 17
        THRESHOLD = 65  # 47
        HYSTERESIS = 15

        self._fan_pin = int(config_data.get('fan_port', FAN_PORT))
        self._hysteresis = int(config_data.get('hysteresis', HYSTERESIS))
        self._temp_threshold = int(config_data.get('threshold', THRESHOLD))
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self._fan_pin, GPIO.OUT)
        GPIO.output(self._fan_pin, GPIO.LOW)

        log('fan_port: {}'.format(self._fan_pin))
        log('threshold: {}'.format(self._temp_threshold))
        log('hysteresis: {}'.format(self._hysteresis))

        self._running = False
        
        self._lock = threading.Lock()
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self._fan_pin, GPIO.OUT)
        GPIO.output(self._fan_pin, GPIO.LOW)

    def _control_loop(self):

        while self._running:
            cpu = CPUTemperature()

            out = None
            if cpu.temperature >= self._temp_threshold:
                out = 1
            elif cpu.temperature <= self._temp_threshold - self._hysteresis:
                out = 0

            if out != None and GPIO.input(self._fan_pin) != out:
                log('FAN {} temp: {}C'.format('ON' if out else 'OFF', cpu.temperature))
                GPIO.output(self._fan_pin, out)

            time.sleep(1.0)

    def start(self):
        
        if not self._running:
            self._running = True
            
            self._thread = threading.Thread(target=self._control_loop, daemon=True)
            self._thread.start()

    def stop(self):
        
        self._running = False
        if hasattr(self, '_thread') and self._thread.is_alive():
            self._thread.join()
