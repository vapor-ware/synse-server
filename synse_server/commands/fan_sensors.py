"""Command handler for the `fan sensor` route."""

import datetime
from collections import OrderedDict

from synse_server import cache
from synse_server.commands.read import read
from synse_server.log import logger


# TODO: Need a note in the configuration files about auto_fan relying on
# device information names in order to find these sensors.
def _translate_device_info(device_info):
    """This translates the device info of the scan device to the field output
    in a fan sensors result set.

    Args:
        device_info (str): The info field of the device in a scan.

    Returns:
        str: The field output in a fan sensors result set.
        None: Unknown device info.
    """
    if device_info.startswith('Rack Temperature 0 '):
        return 'thermistor_0'
    if device_info.startswith('Rack Temperature 1 '):
        return 'thermistor_1'
    if device_info.startswith('Rack Temperature 2 '):
        return 'thermistor_2'
    if device_info.startswith('Rack Temperature 3 '):
        return 'thermistor_3'
    if device_info.startswith('Rack Temperature 4 '):
        return 'thermistor_4'
    if device_info.startswith('Rack Temperature 5 '):
        return 'thermistor_5'
    if device_info.startswith('Rack Temperature 6 '):
        return 'thermistor_6'
    if device_info.startswith('Rack Temperature 7 '):
        return 'thermistor_7'
    if device_info.startswith('Rack Temperature 8 '):
        return 'thermistor_8'
    if device_info.startswith('Rack Temperature 9 '):
        return 'thermistor_9'
    if device_info.startswith('Rack Temperature 10 '):
        return 'thermistor_10'
    if device_info.startswith('Rack Temperature 11 '):
        return 'thermistor_11'

    if device_info == 'Rack Differential Pressure Bottom':
        return 'differential_pressure_0'
    if device_info == 'Rack Differential Pressure Middle':
        return 'differential_pressure_1'
    if device_info == 'Rack Differential Pressure Top':
        return 'differential_pressure_2'

    logger.error('Unknown device_info: {}').format(device_info)
    return None


async def fan_sensors():
    """The handler for the Synse Server "fan sensors" API command.

    Returns:
        dict: A dictionary of device readings for all fan sensors.
    """
    # Auto fan uses the MAX11610 thermistors and SDP619 differential pressure
    # sensors. This isn't a *great* way of doing things since its hardcoded,
    # but this should be enough to get things in place and working in the short
    # term.
    #
    # In the long term, it would be good to expand read functionality in some
    # way such that we can do something like:
    #
    #   GET synse/2.0/read?type=temperature
    #
    # to read all the devices of a given type or model.

    start_time = datetime.datetime.now()
    _cache = await cache.get_device_info_cache()
    scan_cache = await cache.get_scan_cache()

    readings = []
    new_readings = dict()
    new_readings['racks'] = OrderedDict()

    logger.debug('--- FAN SENSORS start ---')
    for _, v in _cache.items():

        logger.debug('FAN SENSORS')
        is_temp = v.output[0].name.lower() == 'temperature' \
                  and v.metadata['model'].lower() == 'max11610'
        is_pressure = v.output[0].name.lower() == 'pressure' \
                      and v.metadata['model'].lower() == 'sdp610'

        if is_temp or is_pressure:
            rack = v.location.rack # string (vec1-c1-wrigley for example)
            board = v.location.board # string (vec for example)
            device = v.uid # string (uuid - only unique to one rack)

            # Find the device in the scan_cache.
            scan_cache_board = None
            scan_cache_device = None
            scan_cache_rack = next((r for r in scan_cache['racks'] if r['id'] == rack), None)
            if scan_cache_rack is not None:
                scan_cache_board = next(
                    (b for b in scan_cache_rack['boards'] if b['id'] == board), None)
                if scan_cache_board is not None:
                    scan_cache_device = next(
                        (d for d in scan_cache_board['devices'] if d['id'] == device), None)
            logger.debug('scan_cache_rack_id, board_id, device_info: {}, {}, {}'.format(
                scan_cache_rack.get('id', None),
                scan_cache_board.get('id', None),
                scan_cache_device.get('info', None)))

            try:
                resp = await read(rack, board, device)
            except Exception as e:
                logger.warning('Failed to get reading for {}-{}-{} for fan_sensors {}.'.format(
                    rack, board, device, e))
            else:
                single_reading = resp.data # Single sensor reading.
                logger.debug('fan_sensors data: {}.'.format(single_reading))
                # Wedge in the VEC name that we received this data from.
                # That way auto_fan can map the data to a VEC.
                single_reading['location'] = {
                    'rack': rack,
                    'board': board,
                    'device': device,
                }
                single_reading['scan_cache_device'] = scan_cache_device
                logger.debug('fan_sensors data with vec: {}.'.format(single_reading))
                readings.append(single_reading)

                # If the rack is not a key in new readings, add it.
                if rack not in new_readings['racks']:
                    new_readings['racks'][rack] = dict()

                # Translate single_reading['scan_cache_device']['info']
                # and add it under the rack key which is:
                # new_readings['racks'][rack][translation] \
                #     = single_reading['data'][0]['value']
                logger.debug('single_reading: {}'.format(single_reading))
                logger.debug(
                    'single_reading[scan_cache_device][info]: {}'.format(
                        single_reading['scan_cache_device']['info']))
                logger.debug(
                    'single_reading[data][single_reading[kind][value]: {}'.format(
                        single_reading['data'][0]['value']))

                # Add sensor reading to result set.
                fan_sensor_key = _translate_device_info(single_reading['scan_cache_device']['info'])
                # This only works because thermistors and pressure sensors have exactly one reading.
                reading_value = single_reading['data'][0]['value']
                if fan_sensor_key is not None and reading_value is not None:
                    # Be sure not to overwrite any existing reading in the current result set.
                    # That would imply a mapping issue or some other bug.
                    if fan_sensor_key in new_readings['racks'][rack]:
                        message = 'fan_sensors avoiding overwrite of existing reading [{}] at ' \
                                  'new_readings[racks][{}][{}] with [{}]'.format(
                                      new_readings['racks'][rack][fan_sensor_key],
                                      rack, fan_sensor_key, reading_value)
                        logger.error(message)
                        raise ValueError(message)
                    # No existing reading in the result set, safe to add it.
                    new_readings['racks'][rack][fan_sensor_key] = reading_value

    logger.debug('--- FAN SENSORS end ---')
    # Sort the new_readings racks by racks['id']
    new_readings['racks'] = OrderedDict(sorted(new_readings['racks'].items()))

    # Sort each output for each rack so we can debug this.
    for rack in new_readings['racks']:
        logger.debug('sorting rack: {}'.format(rack))
        new_readings['racks'][rack] = OrderedDict(sorted(new_readings['racks'][rack].items()))

    end_time = datetime.datetime.now()
    read_time = (end_time - start_time).total_seconds() * 1000

    # Shim in the start, end, read times into each response now that we have them.
    # Even though they are all the same, they didn't used to be and auto fan wants
    # each for logging purposes.
    for rack in new_readings['racks']:
        new_readings['racks'][rack]['start_time'] = str(start_time)
        new_readings['racks'][rack]['end_time'] = str(end_time)
        new_readings['racks'][rack]['read_time'] = read_time

    return new_readings
