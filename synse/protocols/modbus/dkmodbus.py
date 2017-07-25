#!/usr/bin/env python
"""
        \\//
         \/apor IO


        Simple python modbus serial implementation. Originally by Dave Kaplin.
        This is here since pymodbus has a framing issue over serial when the
        client packet is reflected back to the caller, which both the fan and
        CEC board do.
"""

import logging
import struct
import time
from binascii import hexlify

import serial

logger = logging.getLogger(__name__)


class dkmodbus(object):
    """Class that contains the logic and state for this simple modbus
    serial implementation.
    """

    # Modbus function codes.
    _READ_COILS = '\x01'
    _READ_DISCRETE_INPUTS = '\x02'
    _READ_HOLDING_REGISTERS = '\x03'
    _READ_INPUT_REGISTER = '\x04'
    _WRITE_SINGLE_COIL = '\x05'
    _WRITE_SINGLE_REGISTER = '\x06'
    _READ_EXCEPTION_STATUS = '\x07'
    _DIAGNOSTIC = '\x08'
    _WRITE_MULTIPLE_REGISTERS = '\x10'
    _WRITE_MULTIPLE_COILS = '\x0F'
    _GET_COM_EVENT_COUNTER = '\x0B'
    _GET_COM_EVENT_LOG = '\x0C'
    _REPORT_SLAVE_ID = '\x11'
    _READ_FILE_RECORD = '\x14'
    _WRITE_FILE_RECORD = '\x15'
    _MASK_WRITE_REGISTER = '\x16'
    _READ_WRITE_MULTIPLE_REGISTERS = '\x17'
    _READ_FIFO_QUEUE = '\x18'
    _READ_DEVICE_IDENTIFICATION = '\x28'

    # region public

    def __init__(self, serial_device):
        """'
        Create the dkmodbus object for communication over the given serial
        device.
        :param serial_device: The serial device for Modbus communication.
        example: ser = serial.Serial('/dev/ttyUSB3', baudrate=19200,
        parity='E', timeout=0.1)"""
        self.serial_device = serial_device

    def read_holding_registers(self, slave_address, register, register_count):
        """Read one or more registers over modbus.
        :param slave_address: The slave address of the device to read, In
        synse this is unfortunately called device_unit.
        :param register: The first register to read.
        :param register_count: The number of registers to read.
        :returns: A byte array with two bytes per register."""
        slave_address_bytes = struct.pack('>B', slave_address)
        modbus_function_code = dkmodbus._READ_HOLDING_REGISTERS
        register_bytes = struct.pack('>H', register)
        register_count_bytes = struct.pack('>H', register_count)
        packet = slave_address_bytes + modbus_function_code + register_bytes + register_count_bytes
        return self._send_receive_packet(packet)

    def read_input_registers(self, slave_address, register, register_count):
        """Read one or more registers over modbus.
        :param slave_address: The slave address of the device to read, In
        synse this is unfortunately called device_unit.
        :param register: The first register to read.
        :param register_count: The number of registers to read.
        :returns: A byte array with two bytes per register."""
        slave_address_bytes = struct.pack('>B', slave_address)
        modbus_function_code = dkmodbus._READ_INPUT_REGISTER
        register_bytes = struct.pack('>H', register)
        register_count_bytes = struct.pack('>H', register_count)
        packet = slave_address_bytes + modbus_function_code + register_bytes + register_count_bytes
        return self._send_receive_packet(packet)

    @staticmethod
    def reset_usb(usb_list):
        """The FTDI driver has a known issue where the USB device under /dev
        will disappear. This will reset the USB and clear the issue.
        Resetting the usb with the serial port open is problematic. /dev/ttyUSB3
        will come up as /dev/ttyUSB4. Also the serial port does not need to be
        reset if the serial_device is open. The serial port only needs to be
        reset when /dev/ttyUSB3 disappears.
        :param usb_list: List of usbs to reset. For our case this is [1, 2]"""
        logger.error('Resetting USB.')  # Something is bad if you need to do this.
        for usb in usb_list:
            for x in range(2):
                bus = '/sys/bus/usb/devices/usb{}/authorized'.format(usb)
                logger.debug('File {}, action {}.'.format(bus, x))
                with open(bus, 'w') as f:
                    f.write('{}'.format(x))
                    time.sleep(.1)
        return 0

    def write_multiple_registers(
            self, slave_address, register, register_count, byte_count, data):
        """Write multiple registers over modbus.
        :param slave_address: The slave address of the device to write, In
        synse this is unfortunately called device_unit.
        :param register: The first register to write.
        :param register_count: The number of registers to write.
        :param byte_count: The number of bytes to write. 1, 2, 4, or 8.
        :param data: The data to write in bytes.
        """
        slave_address_bytes = struct.pack('>B', slave_address)
        modbus_function_code = dkmodbus._WRITE_MULTIPLE_REGISTERS
        register_bytes = struct.pack('>H', register)
        register_count_bytes = struct.pack('>H', register_count)
        byte_count_bytes = struct.pack('>B', byte_count)

        packet = slave_address_bytes + modbus_function_code + register_bytes + \
            register_count_bytes + byte_count_bytes + data
        return self._send_receive_packet(packet)

    # endregion

    # region private

    @staticmethod
    def _calculate_crc(data):
        """:param data: The data to calculate the CRC for."""

        crc = 0xFFFF
        polynomial = 0xA001  # CRC Calculation

        for d in data:
            crc ^= ord(d)
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ polynomial
                else:
                    crc = (crc >> 1)
        logger.debug('Calculated CRC = 0x{:02X}'.format(crc))
        return crc

    @staticmethod
    def _check_crc(data):
        """:param data: The data to check the CRC of."""

        # Do not include the 2 byte crc in crc calculation.
        crc = dkmodbus._calculate_crc(data[:-2])

        # construct the received crc (last two bytes in packet), keep in mind
        # the cec sends it backwards
        rx_crx = data[-1] + data[-2]
        rx_crc = int(hexlify(rx_crx), 16)
        return crc == rx_crc

    def _send_receive_packet(self, packet):
        """Send a packet and then receive the response.
        """
        # Construct the ADU packet containing PDU packet above
        # Calculate CRC and append at the end of the ADU packet
        crc = dkmodbus._calculate_crc(packet)

        # The modbus firmware wants the bytes in the wrong order for the crc
        # Send the LSB first
        char_crc = chr(crc & 0x00FF)

        # concatenate to end of packet
        packet += char_crc

        char_crc = chr((crc & 0xFF00) >> 8)

        # concatenate to end of packet
        packet += char_crc

        logger.debug(
            'Sending Modbus Function code {} to Slave Address {}'.format(
                ord(packet[1]), (ord(packet[0]))))

        # Get the length of the packet sent out the serial port. Use this to
        # fix the issue of the issue of the FT4232H sending a null character
        # between the packet echoed back from the VEC and the packet sent from
        # the cec sensor hub.
        pdu_length = len(packet)

        # Send packet out serial port
        logger.debug('Packet: {}'.format(hexlify(packet)))
        tries = 10
        sleep_time_on_retry = .5  # second(s)
        for attempt in range(tries):
            try:
                logger.debug('Write attempt {}'.format(attempt))
                self.serial_device.write(packet)

                logger.debug('Read attempt {}'.format(attempt))
                response = self.serial_device.read(1024)
                logger.debug('Raw response: {}'.format(hexlify(response)))

                # Separate received packet into the transmitted packet sent
                # by VEC and received packet sent by the CEC. The FT4232H
                # Module keeps adding a NUL character at the end of the
                # transmitted and received packet. Remove it (can't seem to
                # find out why it does this) parse out the VEC Tx packet
                vec_tx_packet = response[:pdu_length]
                logger.debug('Rx VEC:   (echo back) {}'.format(hexlify(vec_tx_packet)))

                # Did the CEC respond to packet request?
                if len(response) - 1 > pdu_length:

                    # Parse out the CEC packet.

                    # Check the byte following the vec echoed packet. It should
                    # contain the beginning of the packet received from the cec
                    # sensor hub which is it's address. If it contains a 0 then
                    # it's an extra null character which can not contain an address
                    # since it's non zero.
                    if ord(response[pdu_length]) == 0:
                        # Null detected.
                        cec_rx_packet = response[pdu_length + 1:len(response)]
                    else:
                        # No null detected.
                        cec_rx_packet = response[pdu_length:len(response)]

                    logger.debug('Rx CEC:   (received) {}'.format(hexlify(cec_rx_packet)))
                    if not self._check_crc(cec_rx_packet):
                        raise ValueError('Modbus CRC Failed.')
                else:
                    raise ValueError('No response over modbus.')

            except (serial.SerialException, ValueError) as e:
                # This retry must re-send. Otherwise we wait for nothing.
                next_attempt = attempt + 1
                if next_attempt < tries:
                    logger.error(e)

                    # Recreate the serial object.
                    logger.error('Recreating serial object (when reading response).')
                    port = self.serial_device.port
                    baudrate = self.serial_device.baudrate
                    parity = self.serial_device.parity
                    timeout = self.serial_device.timeout

                    time.sleep(sleep_time_on_retry)

                    self.serial_device = serial.Serial(
                        port=port, baudrate=baudrate, parity=parity, timeout=timeout)

                    continue  # retry
                else:
                    logger.error('No more retries.')
                    raise e
            break  # for loop

        # Example Response Packet: (fan speed read of zero)
        # 01 slave address
        # 03 function code
        # 02 bytes returned
        # 0000 register data
        # b844 CRC
        bytes_returned = struct.unpack('B', cec_rx_packet[2])[0]
        logger.debug('bytes_returned: {}'.format(bytes_returned))

        function_code = cec_rx_packet[1]
        # TODO: Double check the '\x04' (_READ_INPUT_REGISTER) in the next PR.
        if function_code == dkmodbus._READ_HOLDING_REGISTERS \
                or function_code == dkmodbus._READ_INPUT_REGISTER:
            logger.debug('returning read data')
            result = cec_rx_packet[3:3 + bytes_returned]
            logger.debug('result: {}'.format(hexlify(result)))
            return result
        logger.debug('just returning 0')
        return 0

        # endregion
