#!/usr/bin/env python
""" Context manager for sensor hub access via I2C and RS485

    Author: Erick Daniszewski
    Date:   18 July 2017

    \\//
     \/apor IO
"""

import time
import serial
from mpsse import MPSSE, I2C, ONE_HUNDRED_KHZ, MSB, IFACE_A, GPIOL0
from binascii import hexlify

import constants
import utils


class Hub(object):
    """ The Hub object provides a means of managing context for I2C and
    RS485 connections.

    It manages both the MPSSE connection and Serial connection used by
    each. Additionally, it contains a few methods around configuration
    for the connections.
    """

    def __init__(self, debug=False):
        # the mpsse connection for I2C
        self.vec = None

        # the serial connection for RS485
        self.ser = None

        # store the cec_rx_packet as a class member
        self._cec_rx_packet = '\x00\x00'

        self.debug = debug

    def __enter__(self):
        """ In the Hub context, open MPSSE and Serial connections to use.
        """
        self._open_vec()
        self._open_ser()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Close the MPSSE and Serial connections when leaving the Hub
        context.
        """
        self._close_vec()
        self._close_ser()

    # -- private methods --

    def _open_vec(self):
        """ Open a new mpsse I2C connection.
        """
        self.vec = MPSSE()

        # Port A I2C for PCA9546A
        self.vec.Open(0x0403, 0x6011, I2C, ONE_HUNDRED_KHZ, MSB, IFACE_A)

        # Set RESET line on PCA9546A to high to activate switch
        self.vec.PinHigh(GPIOL0)
        time.sleep(0.001)

    def _open_ser(self):
        """ Open a new serial RS485 connection.
        """
        # open serial port on port C for RS485 Comms
        self.ser = serial.Serial('/dev/ttyUSB3', baudrate=19200, parity='E', timeout=0.040)

    def _close_vec(self):
        """ Close the open mpsse I2C connection.
        """
        if self.vec is not None:
            self.vec.Close()

    def _close_ser(self):
        """ Close the open serial RS485 connection.
        """
        if self.ser is not None:
            self.ser.close()

    def _adu_packet(self, pdu_packet):
        """
        """
        # construct the ADU packet
        packet = chr(constants.MODBUS_SLAVE_ADDRESS) + pdu_packet

        # calculate the CRC and append it to the end of the packet
        crc = utils.crc_calc(packet)

        # the modbus firmware wants the bytes in the wrong order for
        # the crc. send LSB first.
        packet += chr(crc & 0x00FF)
        packet += chr((crc & 0xFF00) >> 8)

        # get the length of the packet sent out the serial port. use
        # this to fix the issue of the issue of the FT4232H sending a
        # null character between the packet echoed back from the VEC
        # and the packet sent from the cec sensor hub
        pdu_length = len(packet)

        if self.debug:
            print 'Sending Modbus function code {} to slave address {}'.format(
                ord(packet[1]), constants.MODBUS_SLAVE_ADDRESS)

        # send packet out serial port
        self.ser.write(packet)

        if self.debug:
            print '\r\nSending:\t{}'.format(hexlify(packet))

        response = self.ser.read(50)

        # separate received packet into the transmitted packet sent by the VEC
        # and the received packet sent by the CEC. the FT4232H module keeps
        # adding a NUL character at the end of the transmitted and received
        # packet. remove it (can't seem to find out why it does this). parse out
        # the VEC Tx packet.
        vec_tx_packet = response[:pdu_length]

        if self.debug:
            print 'Rx VEC:\t {}'.format(hexlify(vec_tx_packet))

        # did the CEC respond to packet request
        if len(response) - 1 > pdu_length:

            # parse out the CEC packet

            # check the byte following the vec echoed packet. it should contain
            # the beginning of the packet received from the cec sensor hub
            # which is it's address. if it contains a 0 then it's an extra null
            # character which can not contain an address since it's non zero

            if ord(response[-1]) == 0:
                # use the following line if using the module or a board that
                # sends an extra null character.
                self.cec_rx_packet = response[pdu_length + 1:len(response) - 1]
            else:
                # use the following if using the FT5232 on board
                self.cec_rx_packet = response[pdu_length:len(response)]

            if self.debug:
                print 'Rx CEC:\t{}'.format(hexlify(self.cec_rx_packet))

            return utils.crc_check(self.cec_rx_packet)
        return False

    # -- public methods --

    def configure_sensors(self):
        """ Convenience method to wrap the configuration of all sensors
        managed by this hub that need it.

        Currently, those sensors are:
            - SDP600 (differential pressure)
            - MAX11608 (thermistor)
        """
        self.configure_sdp600()
        self.configure_max11698()

    def configure_sdp600(self):
        """ Configure the SDP600 differential pressure sensors.
        """
        # reference the class member in local scope variable
        # for quicker lookups
        vec = self.vec

        # configure each DPS for 9 bit resolution. cycle through the
        # 3 sensors connected to each channel on the PCA9546A
        channel = 1

        for x in range(3):
            channel_str = constants.PCA9546_WRITE_ADDRESS + chr(channel)

            vec.Start()
            vec.Write(channel_str)
            vec.Stop()

            # verify channel was set
            vec.Start()
            vec.Write(constants.PCA9546_READ_ADDRESS)
            vec.SendNacks()
            reg = vec.Read(1)
            vec.Stop()

            if self.debug:
                print '\r\nPCA9546A Control Register: 0x{:02X}'.format(ord(reg))

            vec.SendAcks()

            # configure sensor
            # in the application note for changing measurement resolution
            # three things must be met:
            #  1. read the advanced user register
            #  2. define the new register entry according to the desired
            #     resolution
            #  3. write the new value to the advanced register
            vec.Start()
            vec.Write('\x80\xE5')
            vec.Start()
            vec.Write('\x81')

            # at this point the sensor needs to hold the master but the
            # FT4232 doesn't do clock stretching
            time.sleep(0.001)

            # Read the three bytes out of the DPS sensor (two data bytes
            # and crc)
            sense_data = vec.Read(3)
            vec.Stop()

            # write new value for 9 bit resolution (0b000 for bits 9 - 11)
            if utils.crc8(sense_data):
                if self.debug:
                    print 'SDP600 CRC Passed'

                # convert to a hex integer
                sensor_int = int(hexlify(sense_data[:2]), 16)

                # clear bits 9 - 11
                sensor_int &= 0xF1FF
                msb = sensor_int >> 8
                lsb = sensor_int & 0xFF
                register_str = '\x80\xE4' + chr(msb) + chr(lsb)

                vec.Start()
                vec.Write(register_str)
                vec.Stop()
            else:
                if self.debug:
                    print 'SDP600 CRC Failed'

            # set the next channel
            channel <<= 1

    def configure_max11698(self):
        """ Configure MAX11608 for internal reference and conversion on all
        channels.
        """
        # reference the class member in local scope variable
        # for quicker lookups
        vec = self.vec

        # construct channel 3 command based on address
        channel_3 = constants.PCA9546_WRITE_ADDRESS + '\x08'

        # set channel on PCA9546A to 3 for MAX11608
        vec.Start()
        vec.Write(channel_3)
        vec.Stop()

        # verify channel was set
        vec.Start()
        vec.Write(constants.PCA9546_READ_ADDRESS)
        vec.SendNacks()
        reg = vec.Read(1)
        vec.Stop()

        if self.debug:
            print 'PCA9546A Control Register: 0x{:02X}'.format(ord(reg))

        # Configure MAX11608
        #  There are two registers to write to however there is no address.
        #  Bit 7 determines which register gets written; 0 = Configuration
        #  byte, 1 = Setup byte
        vec.SendAcks()
        vec.Start()

        # Following the slave address, write 0xD2 for setup byte and 0x0F
        # for configuration byte. See tables 1 and 2 in MAX11608 for byte
        # definitions but basically sets up for an internal reference and
        # do an a/d conversion all channels
        vec.Write('\x66\xD2\x0F')
        vec.Stop()

    def read_differential_pressure(self):
        """ Read the differential pressure sensors.
        """
        # reference the class member in local scope variable
        # for quicker lookups
        vec = self.vec

        # cycle through the 3 sensors connected to each channel on the PCA9546A
        channel = 1

        # create list to store the pressure readings
        pressure = [0x00, 0x00, 0x00]

        for x in range(3):

            # Convert channel number to string and add to address
            channel_str = constants.PCA9546_WRITE_ADDRESS + chr(channel)
            vec.Start()
            vec.Write(channel_str)
            vec.Stop()

            # verify channel was set
            vec.Start()
            vec.Write(constants.PCA9546_READ_ADDRESS)
            vec.SendNacks()
            reg = vec.Read(1)
            vec.Stop()
            if self.debug:
                print '\r\nPCA9546A Control Register: 0x{:02X}'.format(ord(reg))

            # read DPS sensor connected to the set channel
            vec.SendAcks()
            vec.Start()
            vec.Write('\x80\xF1')
            vec.Start()
            vec.Write('\x81')

            # give DPS610 time for the conversion since clock stretching is
            # not implemented. 1ms seems to work fine, if wonkyness happens
            # may have to increase
            time.sleep(0.001)

            # read the three bytes out of the DPS sensor (two data bytes and crc)
            sense_data = vec.Read(3)
            vec.Stop()

            if self.debug:
                print 'Sensor {} Data: 0x{:02X} 0x{:02X} 0x{:02X}'.format(x + 1, *map(ord, sense_data))

            if utils.crc8(sense_data):
                if self.debug:
                    print 'SDP600 CRC Passed'

                # convert to an integer number
                sensor_int = int(hexlify(sense_data[:2]), 16)

                # value is in 16 bit 2's complement. might be a better way to
                # store this as a signed value in Python but for now this seems
                # to work fine.
                if sensor_int & 0x8000:
                    sensor_int = (~sensor_int + 1) & 0xFFFF
                    sensor_int = -sensor_int

                if self.debug:
                    print 'Pressure = {} Pa'.format(sensor_int)

                pressure[x] = sensor_int

            else:
                if self.debug:
                    print 'SDP600 CRC Failed'

            # set the next channel
            channel <<= 1

        return pressure

    def read_thermistors(self):
        """ Read the thermistor sensors.
        """
        # reference the class member in local scope variable
        # for quicker lookups
        vec = self.vec

        # values used for slop intercept equation for temperature linear fit
        # temperature = slope(ADC_VALUE - X1) + Y1

        # from spreadsheet Sun Thermistor Plot MAX11608
        slope = [-0.07031, -0.076, -0.10448, -0.15476, -0.23077, -0.35135, -0.55556]
        x1 = [656, 399, 259, 171, 116, 77, 58]

        # Y values are common to both thermistors above
        y1 = [18, 38, 53, 67, 80, 94, 105]

        # construct channel 3 command based on address
        channel_3 = constants.PCA9546_WRITE_ADDRESS + '\x08'

        # set channel on PCA9546A to 3 for MAX11608
        vec.Start()
        vec.Write(channel_3)
        vec.Stop()

        # verify channel was set
        vec.Start()
        vec.Write(constants.PCA9546_READ_ADDRESS)
        vec.SendNacks()
        reg = vec.Read(1)
        vec.Stop()

        if self.debug:
            print 'PCA9546A Control Register: 0x{:02X}'.format(ord(reg))

        # send acks again
        vec.SendAcks()

        # initiating a read starts the conversion
        vec.Start()
        vec.Write('\x67')

        # delay for conversion since the libmpsse can't do clock stretching
        time.sleep(0.010)

        # read the 8 channels (2 bytes per channel)
        data = vec.Read(16)
        vec.Stop()

        # combine the upper and lower byte into one string and convert to
        # 10 bit integer for math manipulation
        ad_int_list = [int(hexlify(data[i:i + 2]), 16) & 0x03FF for i in range(0, len(data), 2)]

        # calculate the Linear Fit temperature.
        # equations based on Brian Elect Thermistor Plot MAX11608.xlxs
        temperature = []
        for x in range(8):
            # Region 7
            if ad_int_list[x] >= 656:
                temperature.append(slope[0] * (ad_int_list[x] - x1[0]) + y1[0])

            # Region 6
            elif ad_int_list[x] >= 399:
                temperature.append(slope[1] * (ad_int_list[x] - x1[1]) + y1[1])

            # Region 5
            elif ad_int_list[x] >= 259:
                temperature.append(slope[2] * (ad_int_list[x] - x1[2]) + y1[2])

            # Region 4
            elif ad_int_list[x] >= 171:
                temperature.append(slope[3] * (ad_int_list[x] - x1[3]) + y1[3])

            # Region 3
            elif ad_int_list[x] >= 116:
                temperature.append(slope[4] * (ad_int_list[x] - x1[4]) + y1[4])

            # Region 2
            elif ad_int_list[x] >= 77:
                temperature.append(slope[5] * (ad_int_list[x] - x1[5]) + y1[5])

            # Region 1
            elif ad_int_list[x] >= 58:
                temperature.append(slope[6] * (ad_int_list[x] - x1[6]) + y1[6])

            # Hit max temperature of the thermistor
            else:
                temperature.append(105.0)

            if self.debug:
                print 'Thermistor Channel {} Temperature: {} C'.format(x, temperature[x])

        return temperature

    def read_temp_humidity(self):
        """ Read the temperature/humidity sensor.
        """
        data_list = [0.0, 0.0]

        # read out input register 0 and 1
        ok = self._adu_packet('\x04\x00\x00\x00\x02')

        if ok:
            # CRC passed calculate temperature and humidity parse out the
            # 2 byte string values into integers
            temperature_raw = int(hexlify(self._cec_rx_packet[3:5]), 16)
            humidity_raw = int(hexlify(self._cec_rx_packet[5:7]), 16)

            # C = -45 + 175 * (raw_temperature_value/65535)
            data_list[0] = ((temperature_raw / 65535.0) * 175) - 45

            # RH = 100 * (raw_humidity_value/65535)
            data_list[1] = (humidity_raw / 65535.0) * 100

            if self.debug:
                print '\r\nTemperature = {} C'.format(data_list[0])
                print '\r\nRelative Humidity = {} %'.format(data_list[1])

        return data_list

    def read_air_speed_temp(self):
        """ Read the air speed/temperature sensor.
        """
        data_list = [0, 0.0]

        # Read out input register 8
        ok = self._adu_packet('\x04\x00\x08\x00\x03')

        if ok:
            # CRC passed calculate velocity. parse out the 2 byte string
            # values into integers
            velocity_raw = int(hexlify(self._cec_rx_packet[3:5]), 16)
            temperature_raw = int(hexlify(self._cec_rx_packet[7:9]), 16)

            data_list[0] = velocity_raw

            # C = temperature_raw/100
            data_list[1] = temperature_raw / 100.0

            if self.debug:
                print '\r\nVelocity = {} mm/s'.format(data_list[0])
                print '\r\nAmbient Temperature = {} C'.format(data_list[1])

        return data_list
