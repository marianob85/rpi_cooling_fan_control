# raspberry-pi-cooling-fan-control

Additional features: 
* provided deb package
* default configuration can be override by json file located in: /usr/local/etc/fan_control.json

Required additional packages: python3-systemd, python3-gpiozero

Example configuration:
[
	{
		"type": "threshold",
		"config": {
			"fan_port": "17",
			"threshold": "30",
			"hysteresis": "10"
		}
	},
	{
		"type": "pwm",
		"config": {
			"fan_port": "17",
			"pwm_points": [
				{"temp": 40, "pwm": 0},
				{"temp": 50, "pwm": 50},
				{"temp": 65, "pwm": 100}
			]
		}
	},
	{
		"tacho_pin" : "27"
	},
	{
		"api_port": "8888"
	}
]