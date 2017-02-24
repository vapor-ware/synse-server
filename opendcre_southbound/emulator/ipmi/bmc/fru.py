#!/usr/bin/env python
""" Model for a BMC's FRU

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


class FRU(object):
    """ Model for a BMC's FRU.

    This class contains the state for the FRU and is used by the mock BMC
    in the IPMI emulator. Additionally, it contains convenience methods for
    performing various action on the FRU / FRU data.

    The currently supported IPMI commands for the FRU are:
     * Get FRU Inventory Area Info
     * Read FRU Data
    """
    def __init__(self, inventory_area, device_access, data):
        self.inventory_area = inventory_area
        self.device_access = device_access

        # if the values in the data field are strings, take them to be hex string
        if data and isinstance(data[0], basestring):
            self.data = [int(d, 16) for d in data]
        else:
            self.data = data

    @classmethod
    def from_config(cls, config_file):
        """ Create a FRU object given a configuration file for it.

        Args:
            config_file (str): the path/name containing the FRU configuration.

        Returns:
            FRU: an instance of the FRU object
        """
        if not os.path.isfile(config_file):
            raise ValueError('Specified config file for FRU record not found : {}'.format(config_file))

        # let any exception propagate upwards so the user knows there was a misconfiguration
        with open(config_file, 'r') as f:
            _cfg = json.load(f)

        return FRU(**_cfg)

    def read_fru(self, packet):
        """ Read data from the FRU.

        The read offset and byte count should be defined in the incoming request
        packet.

        Args:
            packet (IPMI): the IPMI packet modeling the Read FRU request.

        Returns:
            list[int]: the bytes corresponding to the FRU Read response data.
        """
        data = packet.data
        fru_id = data[0]
        offset = data[1:3]
        count = data[3]

        # convert the offset from a byte list to an integer value
        _offset = offset[0]
        _offset |= offset[1]

        # read the fru data from the specified offset
        read_data = self.data[_offset:_offset + count + 1]

        return [len(read_data)] + read_data

    def get_fru_inventory_area_info(self):
        """ Get the FRU Inventory Area Info.

        The data returned from this command is specified through the fru.json
        configuration file which is used to initialize the FRU instance.

        Returns:
            list[int]: the bytes corresponding to the Get FRU Inventory Area
                response data.
        """
        inv_area = [(self.inventory_area >> 0) & 0xff, (self.inventory_area >> 8) & 0xff]
        return inv_area + [self.device_access]
