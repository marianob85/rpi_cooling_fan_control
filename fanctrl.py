from gpiozero import CPUTemperature
import RPi.GPIO as GPIO
import time
import signal
from datetime import datetime
import logging
from systemd import journal
import json
import sys
import functools
from fan_control_threshold import FanControlThreshold

TYPE="threshold"
CONF_FILE = "/usr/local/etc/fan_control.json"

logger = logging.getLogger('fan')
logger.addHandler(journal.JournaldLogHandler())
logger.setLevel(logging.INFO)

def log(msg):
    print('{}: {}'.format(datetime.now(), msg))
    logger.info(msg)


def cleanup_and_exit(fan_reader, signum, frame):
    log("Caught terminate signal.")
    
    if fan_reader:
        fan_reader.stop()
        
    GPIO.cleanup()
    
    log("Exit")
    sys.exit(0)

if __name__ == '__main__':

    config_items = []
    try:
        with open(CONF_FILE) as json_file:
            config_items = json.load(json_file)
            log("Using local configuration file: {}".format(CONF_FILE))
            
            # Fallback w przypadku starej konfiguracji słownikowej
            if isinstance(config_items, dict):
                config_items = [config_items]
    except:
        pass

    selected_data = {}
    if config_items:
        if len(sys.argv) > 1:
            requested_type = sys.argv[1]
            for item in config_items:
                if item.get("type") == requested_type:
                    selected_data = item
                    break
            
            if not selected_data:
                log("Warning: Configuration for type '{}' not found. Using empty/default.".format(requested_type))
        else:
            selected_data = config_items[0]

    controlType = selected_data.get('type', TYPE)

    log('type: {}'.format(controlType))
    log('Current temp: {}C'.format(CPUTemperature().temperature))

    controllers = {
        "threshold": lambda: FanControlThreshold(selected_data.get('config', {})),
        # "other": lambda: OtherClass(selected_data.get('config', {}))
    }

    if controlType not in controllers:
        raise ValueError(f"Unknown type: {controlType}")
        
    fan_control = controllers[controlType]()
    fan_control.start()

    handler = functools.partial(cleanup_and_exit, fan_control)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    
    signal.pause()
