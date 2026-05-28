from gpiozero import CPUTemperature
import time
import signal
from datetime import datetime
import logging
from systemd import journal
import json
import sys
import functools
from fan_control_threshold import FanControlThreshold
from fan_tacho_reader import FanTachoReader
from fan_api import FanAPIHandler

TYPE="threshold"
#CONF_FILE = "/usr/local/etc/fan_control.json"
CONF_FILE = "./config/fan_control.json"

logger = logging.getLogger('fan')
logger.addHandler(journal.JournaldLogHandler())
logger.setLevel(logging.INFO)

def log(msg):
    print('{}: {}'.format(datetime.now(), msg))
    logger.info(msg)


def cleanup_and_exit(fan_control, tacho_reader, api_server, signum, frame):
    log("Caught terminate signal.")
    
    if fan_control:
        fan_control.stop()
        
    if tacho_reader:
        tacho_reader.stop()
        
    if api_server:
        api_server.stop()
        
    log("Exit")
    sys.exit(0)



if __name__ == '__main__':
    config_items = []
    try:
        with open(CONF_FILE) as json_file:
            config_items = json.load(json_file)
            log("Using local configuration file: {}".format(CONF_FILE))
    except:
        pass

    selected_data = {}

    requested_type = TYPE
    if len(sys.argv) > 1:
        requested_type = sys.argv[1]


    if config_items:
        for item in config_items:
            if item.get("type") == requested_type:
                selected_data = item
                break
        
        if not selected_data:
            log("Warning: Configuration for type '{}' not found. Using empty/default.".format(requested_type))

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

    tacho_reader = FanTachoReader(config_items)
    tacho_reader.start()

    api_server = FanAPIHandler(config_items, tacho_reader)
    api_server.start()

    handler = functools.partial(cleanup_and_exit, fan_control, tacho_reader, api_server)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    
    signal.pause()
