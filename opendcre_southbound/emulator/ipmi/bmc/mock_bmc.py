#!/usr/bin/env python
""" The stateful object which emulates a BMC and its configurations. This is used
as part of the IPMI emulator to store BMC and session state for emulated IPMI actions.

    Author: Erick Daniszewski
    Date:   08/31/2016
    
    \\//
     \/apor IO

-------------------------------
Copyright (C) 2015-17  Vapor IO

This file is part of OpenDCRE.

OpenDCRE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

OpenDCRE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenDCRE.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import json
import random
import time

from sdr import SDR
from fru import FRU
from protocol.ipmi import IPMI
from protocol.auth import auth_types, AuthRMCP, SessionContext


# netfn constants
class NETFN(object):
    chassis = 0x00
    sensor = 0x04
    application = 0x06
    storage = 0x0a
    picmg = 0x2c


# command constants
# note that some constants have the same value - this is fine
# because they are used under different netfns
class CMD(object):
    get_channel_auth = 0x38
    get_session_challenge = 0x39
    activate_session = 0x3a
    set_session_privilege = 0x3b
    get_hpmx_capabilities = 0x3e
    get_device_id = 0x01
    close_session = 0x3c
    get_chassis_status = 0x01
    chassis_control = 0x02
    chassis_identify = 0x04
    get_sdr_info = 0x20
    reserve_sdr = 0x22
    get_sdr = 0x23
    get_sensor_reading = 0x2d
    get_picmg_properties = 0x00
    get_fru_inventory_area_info = 0x10
    read_fru_data = 0x11
    set_system_boot_opts = 0x08
    get_system_boot_opts = 0x09
    get_system_guid = 0x37
    dcmi_get_power_reading = 0x02
    dcmi_get_capabilities = 0x01
    get_sensor_threshold = 0x27


# signature constants
class SIGNATURE(object):
    picmg = 0x00
    vita = 0x03
    dcmi = 0xdc


# lookup to go from name -> bits for the supported boot devices. the
# string names here are the only supported boot devices currently.
_boot_dev_lookup = {
    'no_override': 0b0000,
    'pxe': 0b0001,
    'hdd': 0b0010
}


class MockBMC(object):
    """ An object which Mocks a BMC.

    This object should be initialized by the BMC Emulator UDP Server and is then
    made available through all stages of processing to be used.

    It contains the logic for handling incoming IPMI requests and generating an
    appropriate response for that request, while also managing state such as
    power state, led state, boot target state, etc.

    The Mock BMC also initializes SDR and FRU instance for the handling of SDR
    and FRU related commands and state storage.
    """
    def __init__(self, username, password, config_dir, debug=False):
        self.debug_mode = debug

        # TODO - for now, only supporting a single user. if needed, this can be
        # subsumed by a dictionary to support multiple users.
        self.username = username
        self.password = password

        # generate the 16-byte system GUID
        self.system_guid = [random.randint(0, 255) for _ in range(16)]

        # set the initial configurations for the mock bmc
        self._bmc_cfg = self._load_config(config_dir)
        self.channel_auth_capabilities = self._encode_channel_auth_capabilities()
        self.device = self._encode_bmc_device()
        self.chassis = self._encode_bmc_chassis()
        self.capabilities = self._encode_bmc_capabilities()
        self.dcmi = self._encode_dcmi_capabilities()

        # get an instance of an SDR for the BMC
        self.sdr = SDR.from_config(os.path.join(config_dir, 'sdr.json'))
        self.sdr.add_entries_from_config(os.path.join(config_dir, 'sdr_entries.json'))

        # get an instance of a FRU for the BMC
        self.fru = FRU.from_config(os.path.join(config_dir, 'fru.json'))

        # map temporary session ids to their challenge
        self._tmp_session = {}

        # maintain a map of active sessions for tracking purposes
        self._active_sessions = {}

    def debug(self, message):
        if self.debug_mode:
            print message

    @staticmethod
    def _load_config(config_dir):
        """ Load in a JSON configuration file for the Mock BMC instance.

        Args:
            config_dir (str): directory containing the configuration files.

        Returns:
            dict: the configuration dictionary loaded from file.
        """
        cfg_path = os.path.join(config_dir, 'bmc.json')
        if not os.path.isfile(cfg_path):
            raise ValueError('Specified config file for BMC not found : {}'.format(cfg_path))

        # let any exception propagate upwards so the user knows there was a misconfiguration
        with open(cfg_path, 'r') as f:
            _cfg = json.load(f)
        return _cfg

    def handle(self, packet):
        """ The workhorse of the BMC - this takes in an IPMI packet passed to it from the
        UDP Server handler and determines which command it is, and what the response should be.

        It surfaces the response data back to the UDP Server Handler which should then wrap the
        response packet in the appropriate headers and send it back to the requester.

        Args:
            packet (IPMI): the IPMI object which represents the incoming request.

        Returns:
            list[int]: a list of bytes constituting the response from the BMC
        """
        # get the bytes that make up the response data
        _r = self._get_response_data(packet)
        if _r is None:
            netfn = packet.target_lun >> 2
            cmd = packet.command
            sig = packet.signature
            raise ValueError('Failed to generate response for request - netfn: {}, cmd: {}, sig: {}'.format(netfn, cmd, sig))
        response_data, raw_data = _r

        # generate frame the data in the response
        response_packet = packet.make_response(response_data, raw_data)
        return response_packet.to_bytes()

    def _get_response_data(self, packet):
        """ Private method to get the data for a response based on the incoming request packet.

        Args:
            packet (IPMI): the IPMI object which represents the incoming request.

        Returns:
            tuple[list[int], bool]: a 2-tuple which specifies the response byte list
                as well as a boolean flag to indicate whether or not the response
                needs to be framed or just send as raw data.
        """
        # the expected return here is a tuple specifying whether or not the provided
        # data should be passed back as a framed packet or whether it should be sent
        # as raw bytes. these variables help make that distinction clear
        FRAMED_PKT = False
        RAW_DATA = True

        # check what kind of packet it is before generating the response
        packet_auth = packet.packet_data.auth_type
        if packet_auth == auth_types.RMCP:
            payload_type = packet.packet_data.payload_type
            if payload_type == 0x10 or payload_type == 0x12 or payload_type == 0x14:
                return packet, RAW_DATA

        # we determine what action to take looking at two (but sometimes three) bits of data
        # off of the ipmi packet - the netfn, command, and signature (if it exists)
        netfn = packet.target_lun >> 2
        command = packet.command
        signature = packet.signature

        # -------------------------------------------------
        # NETFN: Application Request
        # -------------------------------------------------
        if netfn == NETFN.application:

            # Get Channel Authentication Capabilities
            # .......................................
            if command == CMD.get_channel_auth:
                self.debug('>>> Get Channel Authentication Capabilities')
                return self.get_channel_auth_capabilities(packet), FRAMED_PKT

            # Get Session Challenge
            # .....................
            elif command == CMD.get_session_challenge:
                self.debug('>>> Get Session Challenge')
                return self.get_session_challenge(packet), FRAMED_PKT

            # Activate Session
            # ................
            elif command == CMD.activate_session:
                self.debug('>>> Activate Session')
                return self.activate_session(packet), FRAMED_PKT

            # Set Session Privilege Level
            # ...........................
            elif command == CMD.set_session_privilege:
                self.debug('>>> Set Session Privilege')
                return self.set_session_privilege(packet), FRAMED_PKT

            # Close Session
            # .............
            elif command == CMD.close_session:
                self.debug('>>> Close Session')
                return self.close_session(packet), FRAMED_PKT

            # Get Device ID
            # .............
            elif command == CMD.get_device_id:
                self.debug('>>> Get Device ID')
                return self.get_device_id(), FRAMED_PKT

            # Get System GUID
            # ...............
            elif command == CMD.get_system_guid:
                self.debug('>>> Get System GUID')
                return self.get_system_guid(), FRAMED_PKT

            # Unknown or unsupported command
            # ..............................
            else:
                print 'Command {} is unknown or unsupported for Application Request (netfn:{})'.format(hex(command), hex(NETFN.application))

        # -------------------------------------------------
        # NETFN: Chassis Request
        # -------------------------------------------------
        elif netfn == NETFN.chassis:

            # Chassis Identify
            # ................
            if command == CMD.get_chassis_status:
                self.debug('>>> Get Chassis Status')
                return self.get_chassis_status(), FRAMED_PKT

            # Chassis Control
            # ...............
            elif command == CMD.chassis_control:
                self.debug('>>> Chassis Control')
                return self.chassis_control(packet), FRAMED_PKT

            # Chassis Identify
            # ................
            elif command == CMD.chassis_identify:
                self.debug('>>> Chassis Identify')
                return self.chassis_identify(packet), FRAMED_PKT

            # Get System Boot Options
            # .......................
            elif command == CMD.get_system_boot_opts:
                self.debug('>>> Get System Boot Options')
                return self.get_sys_boot_opts(packet), FRAMED_PKT

            # Set System Boot Options
            # .......................
            elif command == CMD.set_system_boot_opts:
                self.debug('>>> Set System Boot Options')
                return self.set_sys_boot_opts(packet), FRAMED_PKT

            # Unknown or unsupported command
            # ..............................
            else:
                print 'Command {} is unknown or unsupported for Chassis Request (netfn:{})'.format(hex(command), hex(NETFN.chassis))

        # -------------------------------------------------
        # NETFN: PICMG Request
        # -------------------------------------------------
        elif netfn == NETFN.picmg:

            # Get HPM.x Capabilities
            # ......................
            if command == CMD.get_hpmx_capabilities:
                self.debug('>>> Get HPM.X Capabilities')
                return self.capabilities['hpm'], RAW_DATA

            # GET PICMG Properties
            # ....................
            elif command == CMD.get_picmg_properties:

                if signature == SIGNATURE.picmg:
                    self.debug('>>> Get PICMG Capabilities')
                    return self.capabilities['picmg'], RAW_DATA

                elif signature == SIGNATURE.vita:
                    self.debug('>>> Get VITA Capabilities')
                    return self.capabilities['vita'], RAW_DATA

            # DCMI Get Capabilities
            # .....................
            elif command == CMD.dcmi_get_capabilities:

                if signature == SIGNATURE.dcmi:
                    self.debug('>>> Get DCMI Capabilities')
                    return self.dcmi_get_capabilities(packet), FRAMED_PKT

            # DCMI Get Power Reading
            # ......................
            elif command == CMD.dcmi_get_power_reading:

                if signature == SIGNATURE.dcmi:
                    self.debug('>>> DCMI Get Power Reading')
                    return self.dcmi_get_power_reading(packet), FRAMED_PKT

            # Unknown or unsupported command
            # ..............................
            else:
                print 'Command {} is unknown or unsupported for PICMG Request (netfn:{})'.format(hex(command), hex(NETFN.picmg))

        # -------------------------------------------------
        # NETFN: Storage Request
        # -------------------------------------------------
        elif netfn == NETFN.storage:

            # Get SDR Repository Info
            # .......................
            if command == CMD.get_sdr_info:
                self.debug('>>> Get SDR Info')
                return self.sdr.get_sdr_repository_info(), FRAMED_PKT

            # Reserve SDR Repository
            # ......................
            elif command == CMD.reserve_sdr:
                self.debug('>>> Reserve SDR')
                return self.sdr.reserve_sdr_repository(packet.session_id), FRAMED_PKT

            # Get SDR
            # .......
            elif command == CMD.get_sdr:
                self.debug('>>> Get SDR')
                return self.sdr.get_sdr_entry(packet), FRAMED_PKT

            # Get FRU Inventory Info Area
            # ...........................
            elif command == CMD.get_fru_inventory_area_info:
                self.debug('>>> Get FRU Inventory Area Info')
                return self.fru.get_fru_inventory_area_info(), FRAMED_PKT

            # Read FRU Data
            # .............
            elif command == CMD.read_fru_data:
                self.debug('>>> Read Fru Data')
                return self.fru.read_fru(packet), FRAMED_PKT

            # Unknown or unsupported command
            # ..............................
            else:
                print 'Command {} is unknown or unsupported for Storage Request (netfn:{})'.format(hex(command), hex(NETFN.storage))

        # -------------------------------------------------
        # NETFN: Sensor/Event Request
        # -------------------------------------------------
        elif netfn == NETFN.sensor:

            # Get Sensor Reading
            # ..................
            if command == CMD.get_sensor_reading:
                self.debug('>>> Get Sensor Reading')
                reading_data = self.sdr.get_sensor_reading(packet, bool(self.chassis['current_power_state']))
                if reading_data is None:
                    # 0xcb - requested sensor, data, or record not present
                    packet.completion_code = 0xcb
                return reading_data, FRAMED_PKT

            # Get Sensor Threshold
            # ....................
            elif command == CMD.get_sensor_threshold:
                self.debug('>>> Get Sensor Threshold')
                reading_data = self.sdr.get_sensor_threshold(packet)
                return reading_data, FRAMED_PKT

            # Unknown or unsupported command
            # ..............................
            else:
                print 'Command {} is unknown or unsupported for Sensor/Event Request (netfn:{})'.format(hex(command), hex(NETFN.sensor))

        # -------------------------------------------------
        # NETFN: Unknown / Unsupported
        # -------------------------------------------------
        else:
            print 'NetFN code {} is unknown or unsupported.'.format(hex(netfn))

    def dcmi_get_capabilities(self, packet):
        """ Process a DCMI get capabilities command.

        Args:
            packet (IPMI): the IPMI packet representing the incoming capabilities
                request.

        Returns:
            list[int]: the bytes which make up the Get Capabilities response.
        """
        data = packet.data
        selector = str(data[0])

        return self.dcmi['capabilities'][selector]

    def dcmi_get_power_reading(self, packet):
        """ Process a DCMI get power reading command.

        Args:
            packet (IPMI): the IPMI packet representing the incoming power reading
                request.

        Returns:
            list[int]: the bytes which make up the Get Power Reading response.
        """
        data = packet.data
        mode = data[0]
        mode_attrs = data[1]

        t = int(time.time())
        ts = [
            (t >> 0) & 0xff,
            (t >> 8) & 0xff,
            (t >> 16) & 0xff,
            (t >> 24) & 0xff
        ]

        if bool(self.chassis['current_power_state']):
            readings = self.dcmi['power']['current_watts']
            if len(readings) > 1:
                reading_idx = self.dcmi['power'].get('next_reading_idx', 0)
                current_watts = readings[reading_idx]
                self.dcmi['power']['next_reading_idx'] = (reading_idx + 1) % len(readings)
            else:
                current_watts = readings
        else:
            current_watts = [0x00, 0x00]

        return [0xdc] \
               + current_watts \
               + self.dcmi['power']['min_watts'] \
               + self.dcmi['power']['max_watts'] \
               + self.dcmi['power']['avg_watts'] \
               + ts + self.dcmi['power']['reporting_interval_ms'] \
               + [1 << 6]  # power reading state

    def close_session(self, packet):
        """ Process a Close IPMI Session request.

        Args:
            packet (IPMI): the IPMI packet representing the incoming Close Session
                request.

        Returns:
            None: implicitly returns None, which is used as a signal upstream that
                no payload data will be sent with the response.
        """
        # the data in the packet should contain 4 bytes which make up the session id
        sess_id = packet.data

        # convert the session id into a byte string instead of the list for easier lookup
        _sess_id = ''.join(map(chr, sess_id))

        if _sess_id in self._active_sessions:
            packet.session_close_ctx = self._active_sessions[_sess_id]['ctx']
            del self._active_sessions[_sess_id]

    def get_session_challenge(self, packet):
        """ Process a Get Session Challenge request.

        Args:
            packet (IPMI): the IPMI packet representing the incoming Get Session
                Challenge request.

        Returns:
            list[int]: the bytes which make up the Get Session Challenge response.
        """
        # the packet data off the request should contain an auth type and username
        # TODO - for now, leaving these unused, but can use them in the future if desired/needed
        auth = packet.data[0]
        username = packet.data[1:]

        # the response for a session challenge is to provide a temporary session id
        # as well as a challenge string. these are generated below.
        temp_id = [random.randint(0, 255) for _ in range(4)]
        challenge = [random.randint(0, 255) for _ in range(16)]

        # string-ify the id so its hashable
        _temp_id = ''.join(map(chr, temp_id))
        self._tmp_session[_temp_id] = challenge

        return temp_id + challenge

    def activate_session(self, packet):
        """ Process an Activate Session request.

        Args:
            packet (IPMI): the IPMI packet representing the incoming Activate
                Session request.

        Returns:
            list[int]: the bytes which make up the Activate Session response.
        """
        auth = packet.data[0]
        priv = packet.data[1]
        challenge = packet.data[2:18]
        outbound_seq = packet.data[18:]

        # first check the challenge
        tmp_session_id = packet.session_id
        _tmp_session_id = ''.join(map(chr, tmp_session_id))

        if _tmp_session_id not in self._tmp_session:
            raise ValueError('Error - temp session id {} not known to BMC'.format(tmp_session_id))

        known_challenge = self._tmp_session[_tmp_session_id]
        if known_challenge != challenge:
            raise ValueError('Error - challenges do not match! {} != {}'.format(known_challenge, challenge))

        # now that its validated, can remove the temp session
        del self._tmp_session[_tmp_session_id]

        session_id = [random.randint(0, 255) for _ in range(2)] + [0x00, 0x00]
        initial_inbound_seq_num = [random.randint(0, 255) for _ in range(2)] + [0x00, 0x00]

        # now we want to set the outbound seq number on the ipmi response. to do that, we
        # decrement the given sequence number by 1 because the ipmi packet's 'make response'
        # method increments by one, but for this response, we will want to use the given value,
        # so -1, +1 gives a delta of 0
        outbound_seq = [outbound_seq[0] - 1] + outbound_seq[1:]
        packet.session_sequence_number = outbound_seq

        # before returning the data payload, update the internal state to track the new session
        _session_id = ''.join(map(chr, session_id))
        self._active_sessions[_session_id].update({
            'outbound_seq': outbound_seq,
            'privilege': priv
        })

        return [auth] + session_id + initial_inbound_seq_num + [priv]

    def set_session_privilege(self, packet):
        """ Process a Set Session Privilege request.

        If the privilege being set is specified as 0x00, we expect no change
        and will only return the current set privilege.

        Args:
            packet (IPMI): the IPMI packet representing the incoming Set Session
                Privilege request.

        Returns:
            list[int]: a list of bytes which make up the Set Session Privilege response.
        """
        # the incoming request is one byte containing the privilege command data in the bit
        # format of:
        #   [7:4] reserved
        #   [3:0] privilege level
        #       0h - no change, return present privilege
        #       1h - reserved
        #       2h - USER level
        #       3h - OPERATOR level
        #       4h - ADMINISTRATOR level
        #       5h - OEM Proprietary level
        #       all other - reserved
        priv = packet.data[0]

        _session = ''.join(map(chr, packet.session_id))
        if priv == 0x00:
            priv = self._active_sessions[_session]['privilege']
        else:
            self._active_sessions[_session]['privilege'] = priv

        return [priv]

    def get_device_id(self):
        """ Process a Get Device ID request.

        The bytes in this response are set in the config file which was used to
        initialize the BMC state.

        Returns:
            list[int]: a list of bytes which make up the Get Device ID response.
        """
        d = self.device
        return [
            d['device_id'],
            d['device_revision'],
            d['device_availability'],
            d['minor_firmware_revision'],
            d['ipmi_version'],
            d['additional_device_support']
        ] + d['manufacturer_id'] + d['product_id']

    def get_system_guid(self):
        """ Process a Get System GUID request.

        Returns:
            list[int]: a list of bytes which make up the Get System GUID response.
        """
        return self.system_guid

    def get_channel_auth_capabilities(self, packet):
        """ Process a Get Channel Authentication Capabilities request.

        The bytes in this response are set in the config file which was used to
        initialize the BMC state.

        Args:
            packet (IPMI): the IPMI packet representing the incoming Get Boot
                Options request.

        Returns:
            list[int]: a list of bytes which make up the Get Channel Authentication
                Capabilities response.
        """
        _channel, _auth = packet.data
        ac = self.channel_auth_capabilities

        # check the lower 4 bits for channel number. if the channel number is 0x0e,
        # we will use the channel in the config, otherwise we will use the provided
        # channel number.
        if _channel & 0b1111 == 0x0e:
            channel = ac['channel']
        else:
            channel = _channel & 0b1111

        return [
            channel,
            ac['version_compatibility'],
            ac['user_capabilities'],
            ac['supported_connections']
        ] + ac['oem_id'] + [ac['oem_auxiliary_data']]

    def get_chassis_status(self):
        """ Process a Get Chassis Status request.

        The bytes in this response are set in the config file which was used to
        initialize the BMC state.

        Returns:
            list[int]: a list of bytes which make up the Get Chassis Status response.
        """
        c = self.chassis
        return [
            c['current_power_state'],
            c['last_power_event'],
            c['misc_state']
        ]

    def get_sys_boot_opts(self, packet):
        """ Process a Get System Boot Options request.

        Args:
            packet (IPMI): the IPMI packet representing the incoming Get Boot
                Options request.

        Returns:
            list[int]: a list of bytes which make up the Get System Boot
                Options response.
        """
        boot_opt_selector, set_selector, block_selector  = packet.data

        # per IPMI spec, parameter version should always be 0x01
        parameter_version = 0x01

        # set the boot flag as valid
        permanency = 1 << 7

        boot_device = self.chassis['bootdev'] << 2
        bios_verbosity = 0x00
        bios_shared_mode_override = 0x00
        reserved = 0x00

        return [
            parameter_version,
            boot_opt_selector,
            permanency,
            boot_device,
            bios_verbosity,
            bios_shared_mode_override,
            reserved
        ]

    def set_sys_boot_opts(self, packet):
        """ Process a Set System Boot Options request.

        Args:
            packet (IPMI): the IPMI packet representing the incoming Set Boot
                Options request.

        Returns:
            list[int]: a list of bytes which make up the Set System Boot
                Options response.
        """
        boot_opt_selector = packet.data[0]

        # for now, we will only care about selector 5, since that is where the boot device
        # is stored - everything else seems behavioral
        if boot_opt_selector == 0x05:
            data = packet.data[1:]
            boot_num = (data[1] & 0b00111100) >> 2
            self.chassis['bootdev'] = boot_num

    def chassis_control(self, packet):
        """ Process a Chassis Control (power control) request.

        Args:
            packet (IPMI): the IPMI packet representing the incoming Chassis
                Control request.

        Returns:
            list[int]: a list of bytes which make up the Chassis Control response.
        """
        # when issuing a control command, the packet should come in with one byte of
        # data which contains the control operation
        #   [7:4] - reserved
        #   [3:0] - chassis control
        #       0h - power down
        #       1h - power up
        #       2h - power cycle
        #       3h - hard reset
        #       4h - pulse diagnostic interrupt
        #       5h - soft shutdown

        # NOTE - for now, only power down, power up, power cycle, and hard reset
        # are supported.
        control = packet.data[0]

        # Power Down
        if control == 0x00:
            self.chassis['current_power_state'] &= 0b11111110

        # Power Up
        elif control == 0x01:
            self.chassis['current_power_state'] |= 0b01

        # Power Cycle | Hard Reset
        elif control in [0x02, 0x03]:
            # in this case, we will not do anything as the end state should be the
            # same as the current state
            pass

        else:
            print 'Unsupported chassis control operation: {}'.format(hex(control))

    def chassis_identify(self, packet):
        """ Process a Chassis Identify (LED) request.

        Args:
            packet (IPMI): the IPMI packet representing the incoming Chassis Identify
                request.

        Returns:
            list[int]: a list of bytes which make up the Chassis Identify response.
        """
        # here, bits [5:4] specify the identify state, where
        #   00b = off
        #   01b = temporary (timed) on
        #   10b = indefinite on
        #   11b = reserved
        # NOTE - to keep things simple for now, will not time out the identify state
        # if it is temporary on. this can be added in the future if desired, however.
        misc_state = self.chassis['misc_state']

        # for this command, we don't care what the previous identify state is, so for
        # ease of setting it, we first zero out the pertinent bits
        misc_state &= 0b11001111

        if packet.data is None:
            # the default behavior w/ no data is to blink w/ interval 15s
            misc_state |= 0b01 << 4
        else:
            if len(packet.data) == 1:
                identify_interval = packet.data[0]
                # having the interval set to 0x00 means it should turn off indefinitely,
                # we have already accomplished that case by zeroing out the identify state
                # bits, above, so we only care about the other case here.
                if identify_interval != 0x00:
                    # todo - once we add support for actual timeout, the timeout interval
                    # should actually be stored.
                    misc_state |= 0b01 << 4

            # in this case, the only other valid option would be 2 bytes
            else:
                identify_interval, force_identify = packet.data
                if force_identify & 0b01 == 1:
                    misc_state |= 0b10 << 4
                else:
                    # having the interval set to 0x00 means it should turn off indefinitely,
                    # we have already accomplished that case by zeroing out the identify state
                    # bits, above, so we only care about the other case here.
                    if identify_interval != 0x00:
                        # todo - once we add support for actual timeout, the timeout interval
                        # should actually be stored.
                        misc_state |= 0b01 << 4

        # update internal LED state with the updated state
        self.chassis['misc_state'] = misc_state

    def _encode_bmc_device(self):
        """ Encode the BMC device values.

        These values are taken from the raw configurations read in from JSON
        file and converted appropriately for internal use.

        Returns:
            dict: a dictionary containing the properly encoded information for the
                BMC device info.
        """
        if not isinstance(self._bmc_cfg, dict) or 'device' not in self._bmc_cfg:
            raise ValueError('Invalid BMC configuration - must be a dictionary with a "device" field.')

        device_cfg = self._bmc_cfg['device']

        # here, we will not handle key errors so they propagate upward to let the user know of a misconfiguration
        _mfcr_id = device_cfg['manufacturer_id']
        _prod_id = device_cfg['product_id']

        device = {
            'device_id': int(device_cfg['device_id'], 16),
            'device_revision': int(device_cfg['device_revision'], 16),
            'device_availability': int(device_cfg['device_availability'], 16),
            'minor_firmware_revision': int(device_cfg['minor_firmware_revision'], 16),
            'ipmi_version': int(device_cfg['ipmi_version'], 16),
            'additional_device_support': int(device_cfg['additional_device_support'], 16),
            'manufacturer_id': [
                (_mfcr_id >> 0) & 0xff,
                (_mfcr_id >> 8) & 0xff,
                (_mfcr_id >> 16) & 0xff
            ],
            'product_id': [
                (_prod_id >> 0) & 0xff,
                (_prod_id >> 8) & 0xff,
            ]
        }
        return device

    def _encode_bmc_capabilities(self):
        """ Encode the BMC capabilities values.

        These values are taken from the raw configurations read in from JSON
        file and converted appropriately for internal use.

        Returns:
            dict: a dictionary containing the properly encoded information for the
                BMC capabilities.
        """
        if not isinstance(self._bmc_cfg, dict) or 'capabilities' not in self._bmc_cfg:
            raise ValueError('Invalid BMC configuration - must be a dictionary with a "capabilities" field.')

        capabilities_cfg = self._bmc_cfg['capabilities']

        # here, we will not handle key errors so they propagate upward to let the user know of a misconfiguration
        capabilities = dict()
        for capability, byte_list in capabilities_cfg.iteritems():
            capabilities[capability] = [int(i, 16) for i in byte_list]
        return capabilities

    def _encode_bmc_chassis(self):
        """ Encode the BMC chassis values.

        These values are taken from the raw configurations read in from JSON
        file and converted appropriately for internal use.

        Returns:
            dict: a dictionary containing the properly encoded information for the
                BMC chassis.
        """
        if not isinstance(self._bmc_cfg, dict) or 'chassis' not in self._bmc_cfg:
            raise ValueError('Invalid BMC configuration - must be a dictionary with a "chassis" field.')

        chassis_cfg = self._bmc_cfg['chassis']

        # here, we will not handle key errors so they propagate upward to let the user know of a misconfiguration
        chassis = {
            'current_power_state': int(chassis_cfg['current_power_state'], 16),
            'last_power_event': int(chassis_cfg['last_power_event'], 16),
            'misc_state': int(chassis_cfg['misc_state'], 16),
            'bootdev': _boot_dev_lookup.get(chassis_cfg['bootdev'], 0b0000)  # defaults to no_override
        }
        return chassis

    def _encode_channel_auth_capabilities(self):
        """ Encode the BMC channel authentication capability values.

        These values are taken from the raw configurations read in from JSON
        file and converted appropriately for internal use.

        Returns:
            dict: a dictionary containing the properly encoded information for the
                BMC channel auth capabilities.
        """
        if not isinstance(self._bmc_cfg, dict) or 'channel_auth_capabilities' not in self._bmc_cfg:
            raise ValueError('Invalid BMC configuration - must be a dictionary with a "channel_auth_capabilities" field.')

        auth_capabilities = self._bmc_cfg['channel_auth_capabilities']

        # here, we will not handle key errors so they propagate upward to let the user know of a misconfiguration
        _oem_id = auth_capabilities['oem_id']

        capabilities = {
            'channel': int(auth_capabilities['channel'], 16),
            'version_compatibility': int(auth_capabilities['version_compatibility'], 16),
            'user_capabilities': int(auth_capabilities['user_capabilities'], 16),
            'supported_connections': int(auth_capabilities['supported_connections'], 16),
            'oem_auxiliary_data': int(auth_capabilities['oem_auxiliary_data'], 16),
            'oem_id': [
                (_oem_id >> 0) & 0xff,
                (_oem_id >> 8) & 0xff,
                (_oem_id >> 16) & 0xff
            ]
        }
        return capabilities

    def _encode_dcmi_capabilities(self):
        """ Encode DCMI values specified for the supported commands.

        These values are taken from the raw configurations read in from JSON
        file and converted appropriately for internal use.

        Returns:
            dict: a dictionary containing the properly encoded information for DCMI
                actions.
        """
        if not isinstance(self._bmc_cfg, dict) or 'dcmi' not in self._bmc_cfg:
            raise ValueError('Invalid DCMI configuration - must be a dictionary with a "dcmi" field.')

        dcmi_info = self._bmc_cfg['dcmi']

        def watts_to_tuple(current_watts):
            if isinstance(current_watts, list):
                ret = []
                for val in current_watts:
                    ret.append([
                        (val >> 0) & 0xff,
                        (val >> 8) & 0xff
                    ])
                return ret

            else:
                return [
                    [
                        (current_watts >> 0) & 0xff,
                        (current_watts >> 8) & 0xff
                    ]
                ]

        dcmi = {
            'power': {
                'current_watts': watts_to_tuple(dcmi_info['power']['current_watts']),
                'min_watts': [
                    (dcmi_info['power']['min_watts'] >> 0) & 0xff,
                    (dcmi_info['power']['min_watts'] >> 8) & 0xff
                ],
                'max_watts': [
                    (dcmi_info['power']['max_watts'] >> 0) & 0xff,
                    (dcmi_info['power']['max_watts'] >> 8) & 0xff
                ],
                'avg_watts': [
                    (dcmi_info['power']['avg_watts'] >> 0) & 0xff,
                    (dcmi_info['power']['avg_watts'] >> 8) & 0xff
                ],
                'reporting_interval_ms': [
                    (dcmi_info['power']['reporting_interval_ms'] >> 0) & 0xff,
                    (dcmi_info['power']['reporting_interval_ms'] >> 8) & 0xff,
                    (dcmi_info['power']['reporting_interval_ms'] >> 16) & 0xff,
                    (dcmi_info['power']['reporting_interval_ms'] >> 24) & 0xff
                ],
            },
            'capabilities': {
                '1': [int(i, 16) for i in dcmi_info['capabilities']['1']],
                '2': [int(i, 16) for i in dcmi_info['capabilities']['2']],
                '3': [int(i, 16) for i in dcmi_info['capabilities']['3']],
                '4': [int(i, 16) for i in dcmi_info['capabilities']['4']],
                '5': [int(i, 16) for i in dcmi_info['capabilities']['5']]
            }
        }
        return dcmi
