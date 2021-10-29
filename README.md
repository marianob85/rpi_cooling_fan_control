# raspberry-pi-cooling-fan-control

Fork of original project: https://github.com/hobbylad/rpi_cooling_fan_control

Additional features: 
* provided deb package
* default configuration can be override by json file located in: /usr/local/etc/fan_control.json

```json
{
	"fan_port":"17",
	"threshold":"65",
	"hysteresis":"15"
}
```