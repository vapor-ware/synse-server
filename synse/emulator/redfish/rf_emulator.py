#!/usr/bin/env python
""" Redfish Emulator

Starts up the flask app and serves resources. Reads in parameters from
emulator_config.json and passes it to the server with those values
unless they are overridden on start up.

This was based off of DMTF's Redfish-Profile-Simulator (see LICENSE.txt
in the redfish emulator directory, and attribution, below):
https://github.com/DMTF/Redfish-Profile-Simulator

    Author:  Linh Hoang
    Date:    02/09/17

    \\//
     \/apor IO

-------------------------------------------------------

Copyright (c) 2016, Contributing Member(s) of Distributed
Management Task Force, Inc.. All rights reserved.

Redistribution and use in source and binary forms, with or
without modification, are permitted provided that the following
conditions are met:

- Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in
  the documentation and/or other materials provided with the distribution.
- Neither the name of the Distributed Management Task Force (DMTF)
  nor the names of its contributors may be used to endorse or promote
  products derived from this software without specific prior written
 permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.
"""
import os
import sys
import getopt
import json


def main():
    with open('emulator_config.json') as f:
        config = json.load(f)

    host = config['HOST']
    port = config['PORT']
    mockup = config['SOURCE']
    tokens = config['TOKEN']
    mockup_list = os.listdir("./Resources")

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'h:p:m:', ['host=', 'port=', 'mockup='])
    except getopt.GetoptError:
        print 'Unrecognized input, failed to pass in arguments,'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--host'):
            host = arg
        elif opt in ('-p', '--port'):
            port = int(arg)
        elif opt in ('-m', '--mockup'):
            mockup = arg
        else:
            print 'Error, unsupported option given.'
            sys.exit(2)

    print '----------------------------------------------------------------------'
    print 'Starting redfish emulator with host: {}'.format(host)
    print 'At port: {}'.format(port)
    print 'With mockup version: {}'.format(mockup)
    print '----------------------------------------------------------------------'

    if mockup in mockup_list:
        from basic_server import basic_server
        import redfish_resources

        mockup_path = os.path.normpath('./Resources/{}'.format(mockup))
        root_path = os.path.normpath('redfish/v1')

        redfish_resources.get_all_resources(mockup)
        basic_server(mockup_path, root_path, host_name=host, port_number=port, tokens=tokens)
    else:
        print 'No mockup files named "{}" found in Resources directory.'.format(mockup)


if __name__ == '__main__':
    main()
