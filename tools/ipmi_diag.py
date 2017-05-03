#!/usr/bin/env python
""" Diagnostics tool to verify IPMI compatibility.

    To Run:  Just run ./ipmi_diag.py - this tool will then prepare its environment, download the relevant Docker
            image (vaporio/opendcre), gather the necessary BMC information and prop it into the OpenDCRE service on
            startup.  From there, the output of OpenDCRE is validated, providing information on available
            capabilities.  If errors are encountered, check the /logs directory in the OpenDCRE container (this is
            mounted in from /tmp on the local system as a shortcut), or contact Vapor IO.

    Author:  andrew
    Date:    8/29/2016

    \\//
     \/apor IO

    REQUIREMENTS:

        * MacOS or Linux (Windows not yet supported)
        * Docker for MacOS 1.12.x or greater (not Docker Toolbox).
        * Docker for Linux 1.11.x or greater.
        * docker-py 1.9.0 or greater
        * requests 2.11.1 or greater

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
from docker import Client
from getpass import getpass
import requests
import json
import time


def cleanup():
    """ Prepare the environment such that no junk is left behind at start/end of execution.

    Returns: None.

    """
    cli = Client(base_url='unix://var/run/docker.sock')
    try:
        print "Stopping OpenDCRE... "
        cli.stop('opendcre')
        print "OpenDCRE stopped."
    except:
        print "Already stopped."

    try:
        print "Removing opendcre container... ",
        cli.remove_container('opendcre')
        print "OpenDCRE container removed."
    except:
        print "OpenDCRE container already removed."


def pull_images():
    """ Use the local Docker binaries to pull the OpenDCRE image desired for use with diagnostics.

    Returns: True if successful, False otherwise.

    """
    print "Pulling OpenDCRE Docker image... "
    try:
        cli = Client(base_url='unix://var/run/docker.sock')
        cli.pull('vaporio/opendcre', 'v1.2.2')
        print "OpenDCRE image pulled OK."
        return True
    except Exception, e:
        print "Error pulling OpenDCRE image: {}".format(e)
        return False


def get_and_save_bmc_info():
    """ Prompt the user for a local BMC IP and credentials, and construct and save the bmc_info.json file to be
    propped into the OpenDCRE test instance.

    Returns: True if successful, False otherwise.

    """
    bmc_config = {'bmcs': []}
    bmc_ip = raw_input("BMC IP Address: ")
    bmc_username = raw_input("BMC Username: ")
    bmc_password = getpass("BMC Password: ")
    bmc_config['bmcs'].append({'bmc_ip': bmc_ip, 'username': bmc_username, 'password': bmc_password,
                               "auth_type": "RAKP_HMAC_SHA1", "integrity_type": "HMAC_SHA1_96",
                               "encryption_type": "AES_CBC_128"})
    with open("/tmp/bmc_config.json", 'w') as f:
        f.write(json.dumps(bmc_config))
    return True


def start_opendcre():
    """ Start the OpenDCRE container, with the appropriate ports exposed and files propped in.  At a minimum, port
    5000 must be opened, and the bmc_info.json file should be propped in as well.

    Returns: True if successful, False otherwise.

    """
    print "Starting OpenDCRE... "
    try:
        cli = Client(base_url='unix://var/run/docker.sock')
        cli.create_container(image='vaporio/opendcre:v1.2.2', detach=True, ports=[5000],
                             volumes=['/opendcre/bmc_config.json', '/logs'], name='opendcre',
                             command='./start_opendcre_plc_emulator.sh',
                             host_config=cli.create_host_config(binds=[
                                 '/tmp/bmc_config.json:/opendcre/bmc_config.json',
                                 '/tmp:/logs'
                             ], port_bindings={
                                 5000: [5000]
                             }))
        cli.start('opendcre')

        # pause briefly to allow bmc scan to complete
        time.sleep(3)

        print "OpenDCRE started successfully."
        return True
    except Exception, e:
        print "Error starting OpenDCRE: {}".format(e)
        return False


def verify_scan():
    """ Verify that the results of a scan command against the local, running OpenDCRE instance with IPMI single-bmc
    configuration returns a set of sensors and devices that can be inspected.  Provide output to the user that
    indicates which sensors and capabilities are available.

    Returns: True if successful, False otherwise.

    """
    print "Verifying OpenDCRE SCAN results... "
    # print available sensors and capabilities
    r = requests.get('http://127.0.0.1:5000/opendcre/1.2/scan')
    scan_results = json.loads(r.text)
    bmcs_found = 0
    for board in scan_results['boards']:
        if 0x40000000 <= int(board['board_id'], 16) <= 0x4FFFFFFF:
            print "  >> IPMI BMC found with ID: {}".format(board['board_id'])
            bmcs_found += 1
            for device in board['devices']:
                if device['device_type'] == 'power':
                    print "    >> Power control supported."
                elif device['device_type'] == 'system':
                    print "    >> Boot target supported."
                elif device['device_type'] == 'led':
                    print "    >> Chassis LED control supported."
                elif device['device_type'] == 'temperature':
                    print "    >> Temperature sensor detected: {}.".format(device['device_info'])
                elif device['device_type'] == 'fan_speed':
                    print "    >> Fan speed sensor detected: {}.".format(device['device_info'])
    if bmcs_found == 0:
        # TODO: it could be possible to extract the log(s) from the container and package them into something
        # to be sent back to Vapor.
        print "  !> No BMCs found. Check /logs/opendcre_debug.log in the OpenDCRE container for errors."
        return False
    print "Scan results verification complete."
    return True


def check_sensors():
    """ For each readable sensor, do a test-read of that sensor.  If the sensor is unreadable, let the user know.
    Unreadable sensors are most often due to the remote system being powered off, but there may also be something
    odd going on in OpenDCRE's pyghmi base.

    Returns: True if successful, False otherwise.

    """
    print "Checking sensors (remote system must be powered ON)... "
    # print temp and fan speed sensor info
    r = requests.get('http://127.0.0.1:5000/opendcre/1.2/scan')
    scan_results = json.loads(r.text)
    bmcs_found = 0
    for board in scan_results['boards']:
        if 0x40000000 <= int(board['board_id'], 16) <= 0x4FFFFFFF:
            bmcs_found += 1
            for device in board['devices']:
                if device['device_type'] == 'temperature':
                    print "  >> Reading temperature sensor ({}): ".format(device['device_info']),
                    r = requests.get('http://127.0.0.1:5000/opendcre/1.2/read/temperature/{}/{}'.
                                     format(board['board_id'], device['device_id']))
                    reading = json.loads(r.text)
                    try:
                        print str(reading['temperature_c']) + ' C'
                    except:
                        print "[Unable to read temperature.]", reading
                elif device['device_type'] == 'fan_speed':
                    print "  >> Reading fan speed sensor ({}): ".format(device['device_info']),
                    r = requests.get('http://127.0.0.1:5000/opendcre/1.2/read/fan_speed/{}/{}'.
                                     format(board['board_id'], device['device_id']))
                    reading = json.loads(r.text)
                    try:
                        print str(reading['speed_rpm'] + ' RPM')
                    except:
                        print "[Unable to read fan speed.]", reading
    return True


def check_power():
    """ Check the presence of the 'power meter' sensor by looking at the output of a power status command.  Non-default
    results for the input_power field imply

    Returns: None.

    """
    print "Checking power capabilities... "
    # determine if power meter sensor is present
    r = requests.get('http://127.0.0.1:5000/opendcre/1.2/scan')
    scan_results = json.loads(r.text)
    bmcs_found = 0
    for board in scan_results['boards']:
        if 0x40000000 <= int(board['board_id'], 16) <= 0x4FFFFFFF:
            bmcs_found += 1
            for device in board['devices']:
                if device['device_type'] == 'power':
                    print "Reading power information..."
                    r = requests.get('http://127.0.0.1:5000/opendcre/1.2/power/{}/{}'.
                                     format(board['board_id'], device['device_id']))
                    reading = json.loads(r.text)
                    try:
                        print "  >> Power status: " + str(reading['power_status'])
                        print "  >> Input power: " + str(reading['input_power'])
                    except:
                        print "[Unable to read power information.]", reading
    return True


def main():
    cleanup()
    try:
        if not pull_images():
            return
        if not get_and_save_bmc_info():
            return
        if not start_opendcre():
            return
        if not verify_scan():
            return
        if not check_sensors():
            return
        if not check_power():
            return
    finally:
        cleanup()

if __name__ == '__main__':
    main()
