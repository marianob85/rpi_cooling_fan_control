import threading
import time
import logging
from gpiozero import CPUTemperature, PWMOutputDevice
from datetime import datetime
from fan_control_base import FanControlBase

logger = logging.getLogger('fan')

def log(msg):
    print('{}: {}'.format(datetime.now(), msg))
    logger.info(msg)

class FanControlPWM(FanControlBase):
    def __init__(self, config_data):

        FAN_PORT = 17
        self._fan_pin = int(config_data.get('fan_port', FAN_PORT))
        
        # Default PWM points if none provided
        default_points = [
            {"temp": 40, "pwm": 0},
            {"temp": 50, "pwm": 50},
            {"temp": 70, "pwm": 100}
        ]
        self._pwm_points = config_data.get('pwm_points', default_points)
        
        # Sort points by temperature just to be sure
        self._pwm_points = sorted(self._pwm_points, key=lambda k: k['temp'])
        
        self._fan = PWMOutputDevice(self._fan_pin, initial_value=0.0)

        log('fan_port: {}'.format(self._fan_pin))
        log('pwm_points: {}'.format(self._pwm_points))

        self._running = False
        self._lock = threading.Lock()

    def _get_pwm_for_temp(self, current_temp):
        if not self._pwm_points:
            return 0.0
            
        if current_temp <= self._pwm_points[0]['temp']:
            return self._pwm_points[0]['pwm'] / 100.0
            
        if current_temp >= self._pwm_points[-1]['temp']:
            return self._pwm_points[-1]['pwm'] / 100.0
            
        # Interpolate between points
        for i in range(len(self._pwm_points) - 1):
            p1 = self._pwm_points[i]
            p2 = self._pwm_points[i+1]
            
            if p1['temp'] <= current_temp <= p2['temp']:
                temp_range = p2['temp'] - p1['temp']
                pwm_range = p2['pwm'] - p1['pwm']
                
                if temp_range == 0:
                    return p2['pwm'] / 100.0
                
                # fraction of the distance between p1 and p2
                fraction = (current_temp - p1['temp']) / temp_range
                
                # interpolated pwm
                calculated_pwm = p1['pwm'] + (pwm_range * fraction)
                return calculated_pwm / 100.0
                
        return 0.0

    def _control_loop(self):
        while self._running:
            cpu = CPUTemperature()
            current_temp = cpu.temperature
                                    
            target_pwm = self._get_pwm_for_temp(current_temp)

            # log when PWM changes significantly
            if abs(self._fan.value - target_pwm) > 0.01:
                log('FAN PWM set to {:.0f}% (temp: {:.1f}C)'.format(target_pwm * 100, current_temp))
                self._fan.value = target_pwm

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

    def get_state(self):
        if not hasattr(self, '_fan'):
            return {}
        return {"pwm": round(self._fan.value * 100, 1)}
