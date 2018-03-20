"""Command handler for the `fan sensor` route.
"""

from synse import cache
from synse.commands.read import read
from synse.log import logger


async def fan_sensors():
    """

    Returns:

    """
    # auto fan uses the MAX11610 thermistors and SDP619 differential pressure
    # sensors. this isn't a *great* way of doing things since its hardcoded,
    # but this should be enough to get things in place and working in the short
    # term.
    #
    # in the long term, it would be good to expand read functionality in some
    # way such that we can do something like:
    #
    #   GET synse/2.0/read?type=temperature
    #
    # to read all the devices of a given type or model.

    _cache = await cache.get_metainfo_cache()

    readings = []

    logger.debug('--- FAN SENSORS start ---')
    for _, v in _cache.items():

        logger.debug('FAN SENSORS')
        logger.info('fan_sensors cache item: {}'.format(v))

        is_temp = v.type.lower() == 'temperature' and v.model.lower() == 'max11610'
        is_pressure = v.type.lower() == 'differential_pressure' and v.model.lower() == 'sdp610'

        if is_temp or is_pressure:
            rack = v.location.rack
            board = v.location.board
            device = v.uid

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
                    'device': device
                }
                logger.debug('fan_sensors data with vec: {}.'.format(single_reading))
                readings.append(single_reading)

    logger.debug('--- FAN SENSORS end ---')
    return readings
