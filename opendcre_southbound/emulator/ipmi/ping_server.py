#!/usr/bin/env python
""" A simple ping server used for debugging the IPMI emulator during development.

    Author: Erick Daniszewski
    Date:   
    
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
import SocketServer
import datetime


class PingRequestHandler(SocketServer.BaseRequestHandler):
    """ Request handler for the BMC Server Emulator. This will take the incoming
    packet and frame it properly before passing it off to the Mock BMC for the
    actual handling of the packet data to make a valid response.
    """
    def handle(self):
        print '@@ [{}]>> PING'.format(datetime.datetime.utcnow())

        sock = self.request[1]
        sock.sendto('ok', self.client_address)


if __name__ == '__main__':

    server_address = ('0.0.0.0', 8282)
    ping_server = SocketServer.UDPServer(server_address, PingRequestHandler)

    print '----------------------------------------------------------------------'
    print 'Configured Ping Server with address: {}'.format(server_address)
    print '----------------------------------------------------------------------'

    try:
        ping_server.serve_forever()
    except Exception as e:
        print e

    print '----------------------------------------------------------------------'
    print 'Ping Server Terminated.'
    print '----------------------------------------------------------------------'

