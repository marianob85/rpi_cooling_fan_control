import threading
import time
import logging
from gpiozero import CPUTemperature, OutputDevice
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
        
        self._fan = OutputDevice(self._fan_pin, initial_value=False)

        log('fan_port: {}'.format(self._fan_pin))
        log('threshold: {}'.format(self._temp_threshold))
        log('hysteresis: {}'.format(self._hysteresis))

        self._running = False
        
        self._lock = threading.Lock()

    def _control_loop(self):

        while self._running:
            cpu = CPUTemperature()

            out = None
            if cpu.temperature >= self._temp_threshold:
                out = 1
            elif cpu.temperature <= self._temp_threshold - self._hysteresis:
                out = 0

            if out is not None and self._fan.value != out:
                log('FAN {} temp: {}C'.format('ON' if out else 'OFF', cpu.temperature))
                self._fan.value = out

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
        if hasattr(self, '_fan'):
            self._fan.close()
