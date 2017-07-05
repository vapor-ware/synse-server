#!/usr/bin/env python
""" A BMC emulator for IPMI simulation and testing.

This emulator is designed to be a multi-threaded UDP server running out of a
Docker container listening on port 623.

    Author: Erick Daniszewski
    Date:   08/29/2016
    
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

import argparse
import SocketServer

from bmc import MockBMC
from protocol.asf import ASF
from protocol.rmcp import RMCP


class BMCRequestHandler(SocketServer.BaseRequestHandler):
    """ Request handler for the BMC Server Emulator. This will take the incoming
    packet and frame it properly before passing it off to the Mock BMC for the
    actual handling of the packet data to make a valid response.
    """
    def handle(self):
        data, socket = self.request
        bmc = self.server.bmc

        # model the incoming RMCP packet
        packet = RMCP(data, bmc)

        # asf packet format
        if packet.is_asf():
            if packet.message.is_presence_ping():
                self.server.debug('>> Presence Ping')
                # make a pong response
                _header = RMCP.asf_header
                _body = ASF.make_pong(
                    # hardcoded here since the pong should always look the same
                    [0x00, 0x00, 0x11, 0xbe, 0x00, 0x00, 0x00, 0x00, 0x81, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                )

                resp = ''.join(map(chr, _header + _body))
                sock = self.request[1]
                sock.sendto(resp, self.client_address)
                self.server.debug('<< Presence Pong')

        # ipmi packet format
        elif packet.is_ipmi():
            ipmi_packet = packet.message

            _header = RMCP.ipmi_header
            try:
                _body = bmc.handle(ipmi_packet)
            except Exception as ex:
                print ex
                raise

            resp = ''.join(map(chr, _header + _body))
            sock = self.request[1]
            sock.sendto(resp, self.client_address)


class BMCServerEmulator(SocketServer.ThreadingUDPServer, object):
    """ A UDP Server which includes a Mock BMC object. This BMC object
    is initialized here, but accessed and used through nearly all stages of
    processing.
    """
    def __init__(self, debug_mode, *args, **kwargs):
        super(BMCServerEmulator, self).__init__(*args, **kwargs)

        self.debug_mode = debug_mode

        # config directory is hardcoded here since this emulator is meant to be
        # run out of the docker container within which this path is valid.
        self.bmc = MockBMC(
            username='ADMIN',
            password='ADMIN',
            config_dir='/emulator/data',
            debug=debug_mode
        )

    def debug(self, message):
        if self.debug_mode:
            print message


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Vapor IO IPMI Emulator')
    parser.add_argument('-p', '--port', type=int, default=623, help='BMC Port')
    parser.add_argument('-d', dest='debug', action='store_true', help='Run emulator in debug mode')

    args = parser.parse_args()

    server_address = ('0.0.0.0', args.port)
    bmc_emulator = BMCServerEmulator(args.debug, server_address, BMCRequestHandler)

    print '----------------------------------------------------------------------'
    print 'Configured BMC Emulator with server address: {}'.format(server_address)
    print ' - Debug Mode: {}'.format(args.debug)
    print 'Serving...'
    print '----------------------------------------------------------------------'

    try:
        bmc_emulator.serve_forever()
    except Exception as e:
        print e

    print '----------------------------------------------------------------------'
    print 'BMC Emulator Terminated.'
    print '----------------------------------------------------------------------'
