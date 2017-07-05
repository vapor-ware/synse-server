#!/usr/bin/env python
""" The model to hold a BMC's SDR state.

    Author: Erick Daniszewski
    Date:   08/31/2016
    
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

import json
import os
from itertools import count


class SDR(object):
    """ Model for a BMC's SDR.

    This class contains the state for an SDR repository and is used by the
    mock BMC in the IPMI emulator. Additionally, it contains convenience
    methods for initializing from config and providing byte arrays for supported
    SDR commands.

    The currently supported IPMI commands for SDR are:
      * Get SDR Repository Info
      * Reserve SDR Repository
      * Get SDR
    """

    def __init__(self, sdr_version, record_count, free_space, latest_addition_ts, latest_erase_ts, operation_support):
        # initialize a dictionary to map session ids to reservation ids
        self.sdr_reservation = {}

        # initialize a map which will be used to contain the SDR entries, where the
        # key is the entry id, and the value is the configuration information associated
        # with that entry (as a dict)
        self.sdr_entries = {}

        # iterator to ensure unique reservation counts
        self.reservation_count = count()

        self.sdr_version = self._encode_version(sdr_version)
        self.record_count = self._encode_record_count(record_count)
        self.free_space = self._encode_free_space(free_space)
        self.latest_addition_ts = self._encode_timestamp(latest_addition_ts)
        self.latest_erase_ts = self._encode_timestamp(latest_erase_ts)
        self.operation_support = int(operation_support, 16) if isinstance(operation_support, basestring) else operation_support

    @classmethod
    def from_config(cls, config_file):
        """ Create an SDR object given a configuration file for it.

        Args:
            config_file (str): the path/name containing the SDR configuration.

        Returns:
            SDR: an instance of the SDR object
        """
        if not os.path.isfile(config_file):
            raise ValueError('Specified config file for SDR record not found : {}'.format(config_file))

        # let any exception propagate upwards so the user knows there was a misconfiguration
        with open(config_file, 'r') as f:
            _cfg = json.load(f)

        return SDR(**_cfg)

    def add_entries_from_config(self, config_file):
        """ Add SDR entries to the SDR from the specified config file.

        Args:
            config_file (str): the path/name containing the SDR entry
        """
        if not os.path.isfile(config_file):
            raise ValueError('Specified config file for SDR Entry record(s) not found : {}'.format(config_file))

        # let any exception propagate upwards so the user knows there was a misconfiguration
        with open(config_file, 'r') as f:
            _cfg = json.load(f)

        entries = _cfg['records']

        # with all entries now available, we want to add in a field to the config which
        # allows us to track the index of the next reading for that given sensor as
        # well as adding in references to the next record, for convenience so we don't
        # have to do it later.
        for i in range(len(entries)):
            record = entries[i]

            # define the key value pair
            k = int(record['id'], 16)
            v = {
                'id': int(record['id'], 16),
                'data': [int(d, 16) for d in record['data']],
                'readings': record['readings'],
                'event_messages': int(record['event_messages'], 16) if record['event_messages'] is not None else None,
                'threshold_comparison': [int(t, 16) for t in record['threshold_comparison']] if record['threshold_comparison'] is not None else None,

                # for convenience, pull out the sensor id
                'sensor_number': int(record['data'][7], 16),

                # add in a 'next read index' to track sensor read position
                'next_read_idx': 0
            }

            # if we are at the last element, the 'next record id' must be 0xffff
            if i + 1 == len(entries):
                next_record_id = [0xff, 0xff]
            else:
                nxt = int(entries[i + 1]['id'], 16)
                next_record_id = [(nxt >> 0) & 0xff, (nxt >> 8) & 0xff]

            v['next_record_id'] = next_record_id

            # add to the map of known entries
            self.sdr_entries[k] = v

    def get_sdr_repository_info(self):
        """ Get a byte list for the SDR repository info response.

        IPMI command: 0x20 (get sdr repository info command)
        IPMI netfn:   0x0a (storage request)

        Returns:
            list[int]: the bytes for a 'get sdr repository info' command response
        """
        return (
            [self.sdr_version] +
            self.record_count +
            self.free_space +
            self.latest_addition_ts +
            self.latest_erase_ts +
            [self.operation_support]
        )

    def reserve_sdr_repository(self, session_id):
        """ Get a byte list for the Reserve SDR repository response.

        IPMI command: 0x22 (reserve sdr repository command)
        IPMI netfn:   0x0a (storage request)

        Args:
            session_id: the session id to map the reservation to.

        Returns:
            list[int]: the bytes for a 'reserve sdr repository' command response
        """
        reservation = self.reservation_count.next()
        _reservation = [(reservation >> 0) & 0xff, (reservation >> 8) & 0xff]
        self.sdr_reservation[''.join(map(chr, _reservation))] = session_id

        return _reservation

    def get_sdr_entry(self, packet):
        """ Get a byte list for the Get SDR command.

        IPMI command: 0x23 (get SDR command)
        IPMI netfn:   0x0a (storage request)

        Args:
            packet (IPMI): the IPMI packet containing the data specifying
                which entry/offset to get.

        Returns:
            list[int]: the bytes for the 'get SDR' command response
        """
        data = packet.data
        session = packet.session_id

        reservation = data[0:2]
        record_id = data[2:4]
        offset = data[4]
        to_read = data[5]

        # first, validate the reservation w/ the session
        _reservation = ''.join(map(chr, reservation))

        # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        # NOTE:
        #  pyghmi does not appear to make reservations on the SDR before requesting
        #  access. it seems that it provides a reservation id of [0x00, 0x00] when
        #  accessing an entry, so here, we will only validate the registration if the
        #  value is something other than 0x0000 so that this will not fail when pyghmi
        #  is run against it
        # ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
        if _reservation != b'\x00\x00':
            if _reservation not in self.sdr_reservation:
                raise ValueError('Reservation {} not found in SDR tracked reservations.'.format(reservation))

            known_session = self.sdr_reservation[_reservation]
            if known_session != session:
                raise ValueError('Session ID does not match that with reservation {}'.format(reservation))

        # now, get out the data from the specified record id
        _id = record_id[0]
        _id |= record_id[1] << 8

        sdr_entry = self.sdr_entries[_id]
        entry_data = sdr_entry['data']

        data_slice = entry_data[offset:offset + to_read + 1]
        next_entry = sdr_entry['next_record_id']

        return next_entry + data_slice

    def get_sensor_reading(self, packet, bmc_state):
        """ Get a reading for the specified sensor.

        IPMI command: 0x2d (get sensor reading command)
        IPMI netfn:   0x04 (sensor/event request)

        Args:
            packet (IPMI): the packet containing the sensor read info.
            bmc_state (bool): True, if the BMC is "on", False if it is "off".

        Returns:
            list[int]: the bytes for the 'get sensor reading' command response.
        """
        sensor_num = packet.data[0]

        entry = None
        for _, v in self.sdr_entries.iteritems():
            if v['sensor_number'] == sensor_num:
                entry = v
                break

        if entry is None:
            # the upstream caller translates a None response to a non-zero completion code
            return None

        # if the BMC is on, get the readings
        if bmc_state:
            if not entry['readings']:
                return None

            reading = entry['readings'][entry['next_read_idx']]
            entry['next_read_idx'] = (entry['next_read_idx'] + 1) % len(entry['readings'])
        # otherwise, the bmc is off, so we return a 0 reading
        else:
            return None

        return [reading, entry['event_messages']] + entry['threshold_comparison']

    def get_sensor_threshold(self, packet):
        """ Get the threshold for the specified sensor.

        IPMI command: 0x27 (get sensor threshold command)
        IPMI netfn:   0x04 (sensor/event request)

        Args:
            packet (IPMI): the packet containing the sensor info.

        Returns:
            list[int]: the bytes for the 'get sensor threshold' command response.
        """
        # FIXME - sensor thresholds should be sensor-specific. for now, will just
        # return 0 for each threshold, however.
        sensor_num = packet.data[0]
        return [
            0x00,  # readable thresholds - setting this bitmask to 0 indicates that
                   # none of the thresholds are readable.
            0x00,  # lower non-critical threshold
            0x00,  # lowe critical threshold
            0x00,  # lower non-recoverable threshold
            0x00,  # upper non-critical threshold
            0x00,  # upper critical threshold
            0x00   # upper non-recoverable threshold
        ]


    @staticmethod
    def _encode_version(version):
        """ Encode the version number as a byte.

        Note, everything will be encoded as if it were decimal form, e.g. 2, "2", "2.0" and 2.0 would
        encode the same way, so both are valid inputs.

        Args:
            version (int | float | str): the sdr version

        Returns:
            int: encoded version value
        """
        if isinstance(version, float):
            version = str(version)
        elif isinstance(version, int):
            version = str(float(version))

        if isinstance(version, basestring):
            major, minor = map(int, version.split('.') if '.' in version else [version, '0'])

            # now we have the major and minor version numbers as ints. they must now be BCD
            # encoded with bits 7:4 holding the Least Significant digit and bits 3:0 holding
            # the Most Significant digit
            _version = major << 0
            _version |= minor << 4
            return _version

        else:
            raise ValueError('SDR version expected to be int or float but was {}'.format(type(version)))

    @staticmethod
    def _encode_record_count(record_count):
        """ Encode the record count to be padded up to 2 bytes.

        Args:
            record_count (int): the number of records the SDR holds.

        Returns:
            list[int]: the encoded record count.
        """
        return [
            (record_count >> 0) & 0xff,
            (record_count >> 8) & 0xff
        ]

    @staticmethod
    def _encode_free_space(free_space):
        """ Encode the free space of the SDR.

        Free space is limited to 2 bytes.

        Args:
            free_space (int): the free soace of the SDR

        Returns:
            list[int]: the encoded free space
        """
        return [
            (free_space >> 0) & 0xff,
            (free_space >> 8) & 0xff
        ]

    @staticmethod
    def _encode_timestamp(timestamp):
        """ Encode the timestamp to a 4 byte width

        Args:
            timestamp (int): timestamp, in seconds

        Returns:
            list[int]: a list of 4 bytes representing the encoded timestamp
        """
        return [
            (timestamp >> 0) & 0xff,
            (timestamp >> 8) & 0xff,
            (timestamp >> 16) & 0xff,
            (timestamp >> 24) & 0xff
        ]
