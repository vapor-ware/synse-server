# Simple demo that runs on one VEC on one wedge.
# Loop through thermistors, find the hottest, and set the LED colors.
# Step up the fan to cool down and change LEDs accordingly.

import datetime
import json
import logging
import os
import sys
import time

from collections import OrderedDict

# Need synse in the path.
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from synse.vapor_common import http  # nopep8

logging.basicConfig()
logger = logging.getLogger()    # Root logger.
logger.setLevel(logging.INFO)
# Turn down these loggers.
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Vec we are running this on.
VEC_IP = 'localhost'
PROTOCOL = 'http://'

SYNSE_NAME = 'synse'
SYNSE_PORT = 5000


def _get_synse_version():
    """Gets the synse version for the VEC_IP machine.
    :returns: The synse version.
    :raises: When synse cannot be connected to."""
    url = PROTOCOL + VEC_IP + ':' + str(5000) + '/synse/version'
    try:
        r = http.get(url)
        response = json.loads(r.text)
        version = response['version']
        return version
    except Exception:
        logger.error(
            'Unable to get synse version from VEC at {}. The container may not be up yet.'.format(
                VEC_IP))
        raise


def _get_synse_prefix():
    """Gets the synse prefix for synse, example:
    http://synse-x64:5000/synse/1.4/
    Trailing slash is included in the result.
    :returns: The synse prefix."""
    version = _get_synse_version()
    url = PROTOCOL + VEC_IP + ':' + str(SYNSE_PORT) + \
          '/' + SYNSE_NAME + '/' + version + '/'
    logger.debug('get_synse_prefix url: {}'.format(url))
    return url


SYNSE_PREFIX = _get_synse_prefix()


def _scan():
    """Does a scan on synse and returns the response.
    :returns: The scan results from synse."""
    r = http.get(_get_synse_prefix() + '/scan')
    result = r.json()
    logger.debug(json.dumps(result, sort_keys=True, indent=4, separators=(',', ': ')))
    return result


def _get_devices_by_type(scan_results, device_type):
    """Get the the devices in the scan results by device_type.
    We need device_type, rack_id, board_id, device_id to form the Synse URL."""
    result = list()
    logger.debug('_get_device_by_type: {}'.format(device_type))
    for rack in scan_results['racks']:
        rack_id = rack['rack_id']
        logger.debug('rack_id: {}'.format(rack_id))
        for board in rack['boards']:
            logger.debug('board: {}'.format(board))
            board_id = board['board_id']
            logger.debug('board_id: {}'.format(board_id))
            devices = board['devices']
            logger.debug('devices: {}'.format(devices))
            for device in devices:
                found_device_type = device['device_type']
                logger.debug('found_device_type: {}'.format(found_device_type))
                if found_device_type == device_type:
                    # Found one. Add to results.
                    found_device = {
                        'device_type': found_device_type,
                        'rack_id': rack_id,
                        'board_id': board_id,
                        'device_id': device['device_id']
                    }
                    result.append(found_device)
    return result


def _read_sensors(sensors):
    """Read sensors via synse URLs.
    Return array of readings from the sensors."""
    results = []
    for sensor in sensors:
        # Create the synse URL.
        url = _get_synse_prefix() + 'read/{}/{}/{}/{}'.format(
            sensor['device_type'],
            sensor['rack_id'],
            sensor['board_id'],
            sensor['device_id'],
        )
        logger.debug('temperature url: {}'.format(url))
        r = http.get(url)
        result = r.json()
        logger.debug('Appending result: {}'.format(result))
        results.append(result)
    return results


def _find_max_temperature_reading(readings):
    """Find the maximum temperature reading in an array of readings."""
    result = -sys.maxint - 1
    for reading in readings:
        temperature = reading['temperature_c']
        if temperature > result:
            result = temperature
    return result


COLORS = OrderedDict(
    [
        ('off', 0x000000),
        ('violet', 0x9400D3),
        ('indigo', 0x4B0082),
        ('blue', 0x0000FF),
        ('green', 0x00FF00),
        ('yellow', 0xFFFF00),
        ('orange', 0xFF7F00),
        ('red', 0xFF0000),
    ]
)


def _color_to_string(color):
    """From the COLORS value, find the key."""
    for name, our_color in COLORS.iteritems():
        if color == our_color:
            return name
    return '0x{:06x}'.format(color)


def _set_led_color(led_controllers, color):
    """Set the LED color to the color based on the key in COLORS.
    No support for blink_state yet."""
    for led_controller in led_controllers:

        logger.info('Setting LED color to {}'.format(color))
        color_setting = COLORS[color]
        # Create the synse URL.
        if color == 'off':
            url = _get_synse_prefix() + '/led/{}/{}/{}/off'.format(
                led_controller['rack_id'],
                led_controller['board_id'],
                led_controller['device_id'],
            )
        else:
            url = _get_synse_prefix() + '/led/{}/{}/{}/on/0x{:06x}/steady'.format(
                led_controller['rack_id'],
                led_controller['board_id'],
                led_controller['device_id'],
                color_setting,
            )
        logger.debug('led url (color {}): {}'.format(color, url))
        http.get(url)


def _test_led_colors(led_controller):
    logger.debug('')
    for color, setting in COLORS.iteritems():
        logger.debug('Setting LED to color {}, setting 0x{:06x}.'.format(
            color, setting))
        _set_led_color(led_controller, color)
    _set_led_color(led_controller, 'off')


def _set_fan_speed(rpm):
    """Set the fan controller to the given speed."""
    # curl http://localhost:4997/vaporcore/1.0/fan/manual/0
    # TODO / NOTE: Chicago/VEC4 happens to be the leader which is where I'm running this.
    # TODO / NOTE: Believe it's running on VEC10 in Austin which is the leader as well.
    logger.info('Setting fan speed to {}'.format(rpm))
    url = 'http://localhost:4997/vaporcore/1.0/fan/manual/{}'.format(rpm)
    logger.debug('fan url (rpm {}): {}'.format(rpm, url))

    http.get(url)
    return rpm


FAN_SPEED_INITIAL = 175  # TODO: 86 for Austin.
FAN_SPEED_STEP = 25      # rpm


def _set_led_color_by_temperature(led_controllers, max_temperature, initial_max_temperature):
    """Set the led color based on the max temperature given."""
    if max_temperature < initial_max_temperature - 1.3:
        _set_led_color(led_controllers, 'off')
    elif max_temperature < initial_max_temperature - 1.1:
        _set_led_color(led_controllers, 'violet')
    elif max_temperature < initial_max_temperature - .9:
        _set_led_color(led_controllers, 'indigo')
    elif max_temperature < initial_max_temperature - .7:
        _set_led_color(led_controllers, 'blue')
    elif max_temperature < initial_max_temperature - .5:
        _set_led_color(led_controllers, 'green')
    elif max_temperature < initial_max_temperature - .3:
        _set_led_color(led_controllers, 'yellow')
    elif max_temperature < initial_max_temperature - .1:
        _set_led_color(led_controllers, 'orange')
    else:
        _set_led_color(led_controllers, 'red')


def main():
    print 'Main start'
    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(seconds=220)
    logger.info(start_time.strftime('start_time: %Y-%m-%d-%H:%M:%S'))
    logger.info(end_time.strftime('start_time: %Y-%m-%d-%H:%M:%S'))

    scan_results = _scan()
    temperature_sensors = _get_devices_by_type(scan_results, 'temperature')
    led_controllers = _get_devices_by_type(scan_results, 'vapor_led')
    fan_controllers = _get_devices_by_type(scan_results, 'vapor_fan')  # TODO: Use.
    logger.info('temperature_sensors: {}'.format(temperature_sensors))
    logger.info('led_controllers: {}'.format(led_controllers))
    logger.info('fan_controllers: {}'.format(fan_controllers))

    fan_speed = _set_fan_speed(FAN_SPEED_INITIAL)

    initial_max_temperature = None

    while datetime.datetime.now() < end_time:
        # Find max temp reading.
        temperatures = _read_sensors(temperature_sensors)
        logger.debug('temperatures: {}'.format(temperatures))
        max_temperature = _find_max_temperature_reading(temperatures)
        logger.info('max_temperature: {}'.format(max_temperature))

        if initial_max_temperature is None:
            initial_max_temperature = max_temperature
            logger.info('initial_max_temperature: {}'.format(initial_max_temperature))

        # Control LED.
        _set_led_color_by_temperature(
            led_controllers, max_temperature, initial_max_temperature)

        time.sleep(10)
        # Step the fan.
        fan_speed = _set_fan_speed(fan_speed + FAN_SPEED_STEP)

    # Shut off the fan. Turn led off.
    _set_fan_speed(0)   # TODO: Should really put it back in auto,
    #  but this is better for demo. Allows temp to cool for restart.

    _set_led_color(led_controllers, 'off')
    print 'Main end'


if __name__ == '__main__':
    main()
