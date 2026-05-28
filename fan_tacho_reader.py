from fan_control_base import FanControlBase
import RPi.GPIO as GPIO
import threading
import time
from datetime import datetime

def log(msg):
    print('{}: {}'.format(datetime.now(), msg))


class FanTachoReader(FanControlBase):
    def __init__(self, config_items):
        tacho_config = {}
        if isinstance(config_items, list):
            for item in config_items:
                if isinstance(item, dict) and 'tacho_pin' in item:
                    tacho_config = item
                    break

        if 'tacho_pin' not in tacho_config:
            raise ValueError("Missing 'tacho_pin' in configuration.")

        self.tacho_pin = int(tacho_config['tacho_pin'])
        self.pulse_count = 0
        self.current_rpm = 0
        
        self._running = False
        
        self._lock = threading.Lock()
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.tacho_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.tacho_pin, GPIO.FALLING, callback=self._pulse_callback)

    def _pulse_callback(self, channel):
        with self._lock:
            self.pulse_count += 1

    def _measure_loop(self):
        while self._running:
            time.sleep(1)
            
            with self._lock:
                pulses = self.pulse_count
                self.pulse_count = 0
            
            # RPM = (pulses / 2) * 60 = pulses * 30
            self.current_rpm = pulses * 30
            log( "rpm: {}".format(self.current_rpm))

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._measure_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self._running = False
        if hasattr(self, '_thread') and self._thread.is_alive():
            self._thread.join()
        GPIO.remove_event_detect(self.tacho_pin)

    def get_rpm(self):
        return self.current_rpm