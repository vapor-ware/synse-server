#!/usr/bin/env python
""" Synse API Endpoint

    Author:  andrew
    Date:    4/8/2015
    Update:  06/11/2015 - Support power control commands/responses. Minor bug
                          fixes and sensor/device renaming. (ABC)
             06/19/2015 - Add locking to prevent multiple simultaneous requests
                          from stomping all over the bus.
             07/20/2015 - v0.7.0 add node information (stub for now)
             07/28/2015 - v0.7.1 convert to python package
             12/05/2015 - Line noise robustness (retries)
             02/23/2016 - Reorganize code to move IPMI and Location capabilities to other modules.
             09/20/2016 - Reorganize code to move device-specific implementations for command
                          handling to the 'devicebus' module.
             09/25/2016 - Break out endpoint definitions from this file into blueprints.

    \\//
     \/apor IO

-------------------------------
Copyright (C) 2015-17  Vapor IO

This file is part of Synse.

Synse is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

Synse is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Synse.  If not, see <http://www.gnu.org/licenses/>.
"""

import datetime
import logging
from itertools import count

import arrow
from flask import Flask, g, jsonify

import synse.constants as const
from synse.blueprints import core, graphql
from synse.devicebus.command_factory import CommandFactory
from synse.devicebus.devices.i2c import *  # pylint: disable=wildcard-import,unused-wildcard-import
from synse.devicebus.devices.ipmi import *  # pylint: disable=wildcard-import,unused-wildcard-import
from synse.devicebus.devices.plc import *  # pylint: disable=wildcard-import,unused-wildcard-import
from synse.devicebus.devices.redfish import *  # pylint: disable=wildcard-import,unused-wildcard-import
from synse.devicebus.devices.rs485 import *  # pylint: disable=wildcard-import,unused-wildcard-import
from synse.devicebus.devices.snmp import *  # pylint: disable=wildcard-import,unused-wildcard-import
from synse.devicebus.fan_sensors import FanSensors
from synse.errors import SynseException
from synse.utils import cache_registration_dependencies, make_json_response
from synse.vapor_common.util import setup_json_errors
from synse.vapor_common.vapor_config import ConfigManager
from synse.vapor_common.vapor_logging import get_startup_logger, setup_logging
from synse.version import __api_version__

cfg = ConfigManager(
    default='/synse/default/default.json',
    override='/synse/override'
)

logger = logging.getLogger(__name__)

# noinspection PyUnresolvedReferences
DEVICES = cfg.devices                       # devicebus interfaces configured for the Synse instance
# noinspection PyUnresolvedReferences
SCAN_CACHE_FILE = cfg.scan_cache_file       # file which the scan cache will be stored in
# noinspection PyUnresolvedReferences
CACHE_TIMEOUT = cfg.cache_timeout           # the time it takes for the cache to expire
# noinspection PyUnresolvedReferences
CACHE_THRESHOLD = cfg.cache_threshold       # the max number of items the cache can store

app = Flask(__name__)
setup_json_errors(app)

# add the api_version to the prefix
PREFIX = const.endpoint_prefix + __api_version__


# Define a mapping of device registrars.
# The key here is the same as the key in the json configuration file for synse.
# The value is a device class that can register the device.
device_registrars = {
    'plc': PLCDevice,
    'ipmi': IPMIDevice,
    'i2c': I2CDevice,
    'rs485': RS485Device,
    'snmp': SnmpDevice,
    'redfish': RedfishDevice
}

###############################################################################


def _count(start=0x00, step=0x01):
    """ Generator whose next() method returns consecutive values until it
    reaches 0xff, then wraps back to 0x00.

    Args:
        start (int): the value at which to start the count
        step (int): the amount to increment the count

    Returns:
        int: the next count value.
    """
    n = start
    while True:
        yield n
        n += step
        n %= 0xff


@app.before_request
def before_synse_request():
    """ Method to perform all pre-request actions.

    Currently, this includes:
        - track request metadata (time received)
    """
    g.request_received = arrow.utcnow().timestamp


################################################################################
# DEBUG METHODS
################################################################################

@app.route(PREFIX + '/test', methods=['GET', 'POST'])
def test_routine():
    """ Test routine to verify the endpoint is running and ok, without
    relying on any backend layer.
    """
    return make_json_response({'status': 'ok'})


@app.route(const.endpoint_prefix + 'version', methods=['GET', 'POST'])
def synse_version():
    """ Get the API version used by Synse.

    This can be used in formulating subsequent requests against the
    Synse REST API.
    """
    return make_json_response({'version': __api_version__})


@app.route(PREFIX + '/plc_config', methods=['GET', 'POST'])
def plc_config():
    """ Test routine to return the PLC modem configuration parameters
    on the endpoint.
    """
    raise SynseException(
        'Unsupported hardware type in use. '
        'Unable to retrieve modem configuration.'
    )


# Global FanSensors object because we do not want to hunt for the sensors on
# each fan_sensors call and we shouldn't have to.
SENSORS = FanSensors()


@app.route(PREFIX + '/fan_sensors', methods=['GET'])
def fan_sensors():
    """Get all sensor data we need for fan control from the VEC."""

    global SENSORS
    sensors = SENSORS
    sensors.initialize(app.config)
    if not sensors.initialized:
        raise SynseException(
            'Unable to read fan_sensors. All devices are not yet registered.'
        )

    sensors.read_sensors()

    # Reading info.
    result = {
        'start_time': str(sensors.start_time),
        'end_time': str(sensors.end_time),
        'read_time': sensors.read_time
    }

    # Sensor data.
    for thermistor in sensors.thermistors:
        if thermistor is not None:
            result[thermistor.name] = thermistor.reading

    for dpressure in sensors.differentialPressures:
        if dpressure is not None:
            result[dpressure.name] = dpressure.reading

    return jsonify(result)


def register_app_devices(application):
    """ Register all devicebus interfaces specified in the Synse config
    file with the Flask application.

    Args:
        application (Flask): the Flask application to register the devices to.
    """
    # before registering any devices, make sure all dependencies are cached
    # globally -- this is needed for any threaded registration.
    cache_registration_dependencies()

    _devices = {}
    _single_board_devices = {}

    app_cache = (_devices, _single_board_devices)

    _failed_registration = False

    for device_interface, device_config in DEVICES.iteritems():
        device_interface = device_interface.lower()

        _registrar = device_registrars.get(device_interface)

        if not _registrar:
            raise ValueError(
                'Unsupported device interface "{}" found during registration.'.format(
                    device_interface)
            )

        try:
            _registrar.register(device_config, application.config, app_cache)
        except Exception as e:
            logger.error('Failed to register {} device: {}'.format(
                device_interface, device_config))
            logger.exception(e)
            _failed_registration = True

    if _failed_registration:
        raise ValueError(
            'Failed to register all configured devices -- check that the device configuration '
            'files are correct.'
        )

    application.config['DEVICES'] = _devices
    application.config['SINGLE_BOARD_DEVICES'] = _single_board_devices


def main(serial_port=None, hardware=None):
    """ Main method to run the flask server.

    Args:
        serial_port (str): specify the serial port to use; the default is fine
            for production, but for testing it is necessary to pass in an emulator
            port here.
        hardware (int): the type of hardware we are working with - see devicebus.py
            for values -> by default we use the emulator, but may use VEC; this
            dictates what type of configuration we do on startup and throughout.
    """
    setup_logging(default_path='/synse/configs/logging/synse.json')

    logger.info('=====================================')
    logger.info('Starting Synse Endpoint')
    logger.info('[{}]'.format(datetime.datetime.utcnow()))
    logger.info('=====================================')

    # get an error logger to log out anything that could cause app startup failure
    startup_logger = get_startup_logger()

    try:
        # FIXME - using app.config here isn't 'wrong', but when Synse changes to be
        #         anything more than single proc/thread, we will want to change this.
        #         flask context objects are not a 'good' solution, so we will need some
        #         thin db/caching layer (likely redis)

        app.config['SERIAL_OVERRIDE'] = serial_port
        app.config['HARDWARE_OVERRIDE'] = int(hardware) if hardware is not None else hardware

        app.config['COUNTER'] = _count(start=0x01, step=0x01)
        app.config['ENDPOINT_PREFIX'] = PREFIX
        app.config['SCAN_CACHE'] = SCAN_CACHE_FILE

        # define board offsets -- e.g. the offset within the board_id space to add to the
        # board_id. this should increase monotonically for each board for each device interface
        # so that each board has a unique id whether registered upfront or at runtime
        app.config['IPMI_BOARD_OFFSET'] = count()
        app.config['I2C_BOARD_OFFSET'] = count()
        app.config['RS485_BOARD_OFFSET'] = count()
        app.config['PLC_BOARD_OFFSET'] = count()
        app.config['SNMP_BOARD_OFFSET'] = count()
        app.config['REDFISH_BOARD_OFFSET'] = count()

        # add a command factory to the app context
        app.config['CMD_FACTORY'] = CommandFactory(app.config['COUNTER'])

        # define device lookup tables - these will be populated during device
        # registration. 'devices' maps a devices' UUID to the devicebus instance.
        # 'single board devices' maps the board id or other alias to the
        # devicebus instance being registered.
        app.config['DEVICES'] = {}
        app.config['SINGLE_BOARD_DEVICES'] = {}

        app.register_blueprint(core)
        app.register_blueprint(graphql)
        register_app_devices(app)

        logger.info('Registered {} Device(s)'.format(len(app.config['DEVICES'])))
        for v in app.config['DEVICES'].values():
            logger.info('... {}'.format(v))

        logger.info('app.config: {}'.format(app.config))
        logger.info('Endpoint Setup and Registration Complete')
        logger.info('----------------------------------------')

    except Exception as e:
        startup_logger.error('Failed to start up Synse endpoint!')
        startup_logger.exception(e)
        raise

    if __name__ == '__main__':
        app.run(host='0.0.0.0')
