#!/usr/bin/env python
""" An RS485 emulator for use in testing RS485 capabilities of OpenDCRE.

    When invoked, takes a single command line argument pointing to the config file to be used by the emulator.

    Author: Andrew Cencini
    Date:   10/11/2016

    \\//
     \/apor IO
"""
from pymodbus.server.sync import ModbusSerialServer

from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore.store import BaseModbusDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

from pymodbus.transaction import ModbusRtuFramer

import json
import logging
import sys

import vapor_common.vapor_logging as vapor_logging

logger = logging.getLogger(__name__)

emulator_config = dict()


class EmulatorDataBlock(BaseModbusDataBlock):
    """ A datablock that keeps state, and can also iterate through a list of values.
    """
    def __init__(self, values):
        self.values = values
        self.address = 0
        self.default_value = 0
        self._state = dict()        # state tracking for cycling through responses

    def _get_next_value(self, address):
        if isinstance(self.values[address], list):
            # if we have a list of values for a given register, add, retrieve and update the state counter
            # for the given address, and return the next value from the list
            self._state[address] = dict() if address not in self._state else self._state[address]
            _count = self._state[address]['_count'] if '_count' in self._state[address] else 0
            val = self.values[address][_count]
            _count += 1
            self._state[address]['_count'] = _count % len(self.values[address])
            return val
        # otherwise, return the register value for the address
        return self.values[address]

    def getValues(self, address, count=1):
        address -= 1    # 0-based addressing for Vapor applications
        logger.debug("GET: Address {} Count {} Values {}".format(address, count, self.values))
        return [self._get_next_value(i) for i in range(address, address + count)]

    def setValues(self, address, values):
        address -= 1    # 0-based addressing for Vapor applications
        logger.debug("SET: Address {} Values {}".format(address, values))
        if isinstance(values, dict):
            for idx, val in values.iteritems():
                self.values[idx] = val
        else:
            if not isinstance(values, list):
                values = [values]
            for idx, val in enumerate(values):
                self.values[address + idx] = val

    def validate(self, address, count=1):
        address -= 1    # 0-based addressing for Vapor applications
        logger.debug("VALIDATE: Address {} Count {}".format(address, count))
        if count == 0:
            return False
        handle = set(range(address, address + count))
        return handle.issubset(set(self.values.iterkeys()))


def main():
    """ The main body of the emulator - listens for incoming requests and processes them.

    Starts by initializing the context from config, then listening on the given serial device.

    :return: None.
    """
    slaves = dict()
    for device in emulator_config['devices']:
        # for each device (unit), create an EmulatorDataBlock that has the register map defined in config

        def _convert_register(v):
            if isinstance(v, list):
                # return a list of converted values
                return [int(x, 16) for x in v]
            else:
                # convert single value to int
                return int(v, 16)

        block = EmulatorDataBlock({int(k, 16): _convert_register(v) for k, v in device['holding_registers'].items()})
        logger.error("Device: {} Block: {}".format(device['device_address'], block.values))
        store = ModbusSlaveContext(di=block, co=block, hr=block, ir=block)
        slaves[device['device_address']] = store

    context = ModbusServerContext(slaves=slaves, single=False)

    for slave in context:
        logger.error("Slaves: {}".format(slave[0]))

    identity = ModbusDeviceIdentification()
    identity.VendorName = 'Vapor IO'
    identity.ProductName = 'OpenDCRE Modbus Emulator'
    identity.MajorMinorRevision = '1.4'

    # this is done to allow us to actually use RTU framing which the Start shortcut prevents
    server = ModbusSerialServer(context, framer=ModbusRtuFramer, identity=identity,
                                port=emulator_config['serial_device'], timeout=0.01)
    server.serve_forever()

if __name__ == '__main__':

    vapor_logging.setup_logging(default_path='logging_emulator.json')

    # the emulator config file is the one and only param passed to the emulator
    emulator_config_file = sys.argv[1]

    # parse and validate config
    with open(emulator_config_file, 'r') as config_file:
        emulator_config = json.load(config_file)

    logger.error('-----------------------------------------------------------------------')
    logger.error('Started RS485 emulator on ({})'.format(emulator_config['serial_device']))
    logger.error('-----------------------------------------------------------------------')

    while True:
        try:
            main()
        except Exception as e:
            logger.error("Exception encountered. (%s)", e)
