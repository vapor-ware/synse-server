#!/usr/bin/env python
""" Flask Server to direct requests.

A basic flask app that serves mockup resources. Specifies what request
methods are supported for specific resources. Emulates behavior of a
Redfish service. Gets requested resources from database generated in
redfish_resources.

This was based off of DMTF's Redfish-Profile-Simulator (see LICENSE.txt
in the redfish emulator directory, and attribution, below) -
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
# pylint: skip-file
# this will need some refactoring in the future, so for now, disabling pylint

import json
import os

from flask import Flask, jsonify, request

from redfish_auth import RfAuthentication
from redfish_resources import database, users
from templates.chassis_template import CHASSIS_TEMPLATE
from templates.power_template import POWER_TEMPLATE


def basic_server(mockup_path, root_path, host_name, port_number, tokens):
    """ Called on emulator start up to create the flask app and direct requests.

    Args:
        mockup_path (str): the file path to the mockup directory in Resources
        root_path (str): the root Redfish URI, e.g. redfish/v1.
        host_name (str): the host to serve on, e.g. '0.0.0.0'.
        port_number (int): the port to serve on, e.g. 5040.
    """
    app = Flask(__name__)
    auth = RfAuthentication()

    @auth.verify_password
    def verify_rf_password(user, password):
        """ Verify the user password.
        """
        if user in users:
            if password == users[user]:
                return True
        return False

    @auth.verify_token
    def verify_rf_token(token):
        """ Verify the user token
        """
        return token in tokens

    @app.errorhandler(404)
    def resource_not_found():
        """ Generate a 'resource not found' message.
        """
        message = {
            'status': 404,
            'message': 'Resource not found.'
        }
        resp = jsonify(message)
        resp.status_code = 404
        return resp

    def get_index_from_database(*args):
        """ Get the Redfish index for a given path.
        """
        path = os.path.normpath('/'.join(args))
        if path in database:
            index = json.dumps(database[path])
            return index
        return resource_not_found()

    @app.route('/', methods=['GET'])
    def root():
        """ Get the response from the Redfish root.
        """
        return get_index_from_database(mockup_path, root_path)

    @app.route('/redfish', methods=['GET'])
    def rf_versions():
        """ Get the Redfish version
        """
        return get_index_from_database(mockup_path, 'redfish')

    @app.route('/redfish/v1', methods=['GET'])
    def rf_version1():
        """ Get the index for the Redfish v1 emulator instance
        """
        return get_index_from_database(mockup_path, root_path)

    @app.route('/redfish/v1/<path:path>', methods=['GET'])
    @auth.auth_required
    def catch_all(path):
        """ Get the Redfish index.
        """
        return get_index_from_database(mockup_path, root_path, path)

    @app.route('/redfish/v1/<collection_name>/<path:path>', methods=['PATCH'])
    @auth.auth_required
    def rf_resource_patch(collection_name, path):
        """ Update a resource in the given collection.
        """
        res_path = os.path.join(mockup_path, root_path, collection_name, path)
        if res_path in database:
            rdata = request.get_json()
            if rdata is not None and isinstance(rdata, dict):
                for key in rdata.keys():
                    if key in database[res_path]:
                        database[res_path].update(rdata)
                        return jsonify({'Resource patched': '{} with {}'.format(
                            os.path.join(root_path, collection_name, path),
                            json.dumps(rdata))}), 200
                return 'Bad payload, no matching key:value found in resource requested.', 400
            return 'Bad payload. Expected json.', 400
        return resource_not_found()

    @app.route('/redfish/v1/<collection_name>/<path:path>', methods=['PUT'])
    @auth.auth_required
    def rf_resource_put(collection_name, path):
        """ Add a new item to the specified Redfish collection.
        """
        res_path = os.path.join(mockup_path, root_path, collection_name, path)
        rdata = request.get_json()
        if rdata is not None:
            # properties not specified in PUT are reset to default values, generally null
            for key in database[res_path]:
                if key in rdata.keys():
                    database[res_path][key] = rdata[key]
                else:
                    database[res_path][key] = 'null'
            return jsonify({'Replaced resource': '{}'.format(path)}), 200
        return 'Bad payload. Expected json.', 400

    @app.route('/redfish/v1/Chassis/<new_object>', methods=['POST'])
    @auth.auth_required
    def rf_chassis_post(new_object):
        """ Create a new Redfish Chassis
        """
        new_path = os.path.join(mockup_path, root_path, 'Chassis', new_object)
        rdata = request.get_json()
        template = CHASSIS_TEMPLATE
        if rdata is not None:
            if new_path not in database:
                for key in rdata:
                    if key in template:
                        template[key] = rdata[key]
                template['@odata.id'] = '/redfish/v1/Chassis/{}'.format(new_object)
                template['Id'] = new_object
                template['Power'] = {
                    '@odata.id': '/redfish/v1/Chassis/{}/Power'.format(new_object)
                }
                template['Thermal'] = {
                    '@odata.id': '/redfish/v1/Chassis/{}/Thermal'.format(new_object)
                }
                database[new_path] = template
                return jsonify(
                    {'Added new resource to Chassis collection': '{}'.format(new_object)}
                ), 200
            return 'Resource already exists, use PUT or PATCH to update ' \
                   'existing resource.', 405
        return 'Bad payload, expected json or json file.', 400

    @app.route('/redfish/v1/Chassis/<new_object>/Power', methods=['POST'])
    @auth.auth_required
    def rf_power_post(new_object):
        """ Change the power status of a Redfish chassis.
        """
        new_path = os.path.join(mockup_path, root_path, 'Chassis', new_object, 'Power')
        rdata = request.get_json()
        template = POWER_TEMPLATE
        if rdata is not None:
            if new_path not in database:
                for key in rdata:
                    if key in template:
                        template[key] = rdata[key]
                template['@odata.id'] = '/redfish/v1/Chassis/{}/Power'.format(new_object)
                database[new_path] = template
                return jsonify(
                    {'Added new Power resource to Chassis object:' '{}'.format(new_object)}), 200
            return 'Resource already exists, use PUT or PATCH to update ' \
                   'existing resource.', 405
        return 'Bad payload, expected json.', 400

    # Create thermal resource for newly created chassis resource

    @app.route('/redfish/v1/Systems/<system_name>/Actions/ComputerSystem.Reset', methods=['POST'])
    @auth.auth_required
    def rf_system_reset(system_name):
        """ Restart a Redfish system.
        """
        path = os.path.join(mockup_path, root_path, 'Systems', system_name)
        rdata = request.get_json()
        if rdata is not None and 'ResetType' in rdata and rdata['ResetType'] in [
                'On',
                'ForceOff',
                'GracefulShutdown',
                'GracefulRestart',
                'ForceRestart',
                'Nmi',
                'ForceOn',
                'PushPowerButton']:
            database[path]['Actions']['#ComputerSystem.Reset'] = {
                'ResetType': rdata['ResetType'],
                'target': '/redfish/v1/Systems/{}/Actions/ComputerSystem.Reset'.format(system_name)
            }
            if rdata['ResetType'] in ['On', 'ForceRestart', 'GracefulRestart']:
                database[path]['PowerState'] = 'On'
                return 'System was reset, power now on.', 200
            database[path]['PowerState'] = 'Off'
            return 'System was reset, power now off.', 200

        return 'Invalid payload, system was not reset.', 400

    @app.route('/redfish/v1/Systems/<system_name>', methods=['PATCH'])
    @auth.auth_required
    def rf_system_boot_target(system_name):
        """ Patch a Redfish system boot target value.
        """
        path = os.path.join(mockup_path, root_path, 'Systems', system_name)
        rdata = request.get_json()

        boot = 'Boot'
        bootsot = 'BootSourceOverrideTarget'

        if isinstance(rdata, dict) and boot in rdata and bootsot in rdata['Boot']:
            if rdata[boot][bootsot] in database[path][boot]['{}@Redfish.AllowableValues'.format(
                    bootsot)]:

                database[path][boot][bootsot] = rdata[boot][bootsot]
                return 'System boot target changed to {}.'.format(rdata[boot][bootsot]), 200

            return 'Invalid boot target value. \n Allowable values are: {}'.format(
                database[path][boot]['{}@Redfish.AllowableValues'.format(bootsot)]), 400

        return 'Invalid payload, expected json.', 400

    @app.route('/redfish/v1/SessionService/Sessions', methods=['POST'])
    def create_rf_session():
        """ Create a new Redfish session.
        """
        sessions_path = os.path.join(mockup_path, root_path, 'SessionService', 'Sessions')
        rdata = request.get_json()
        sess_num = str(database[sessions_path]['Members@odata.count'] + 1)
        if rdata is not None and 'UserName' and 'Password' in rdata:
            new_path = os.path.join(mockup_path, root_path, 'SessionService', 'Sessions', sess_num)
            database[new_path] = {
                '@odata.context': '/redfish/v1/$metadata#Session.Session',
                '@odata.id': '/redfish/v1/SessionService/Sessions/{}'.format(sess_num),
                '@odata.type': '#Session.v1_0_0.Session',
                'Id': '{}'.format(sess_num),
                'Name': 'User Session',
                'Description': 'User Session',
                'UserName': '{}'.format(rdata['UserName'])
            }
            database[sessions_path]['Members@odata.count'] += 1
            database[sessions_path]['Members'].append(
                {'@odata.id': '/redfish/v1/SessionService/Sessions/{}'.format(sess_num)}
            )
            resp = 'Location: /redfish/v1/SessionService/Sessions/{} \n'\
                   'X-Auth-Token: 123456789authtoken \n' \
                   '{}'.format(sess_num, json.dumps(database[new_path]))
            return resp, 200
        return 'Bad payload, expected {"UserName": <username>, \n' \
               '                       "Password": <password>}', 400

    @app.route('/redfish/v1/SessionService/Sessions/<session_name>', methods=['DELETE'])
    def rf_session_logout(session_name):
        """ Log out of redfish session.
        """
        collection_path = os.path.join(mockup_path, root_path, 'SessionService', 'Sessions')
        res_path = os.path.join(collection_path, session_name)
        try:
            del database[res_path]
            database[collection_path]['Members@odata.count'] -= 1
            for item in database[collection_path]['Members']:
                if session_name in item['@odata.id']:
                    database[collection_path]['Members'].remove(item)
            return jsonify({'Session logout': '{}'.format(session_name)}), 200
        except KeyError:
            return 'Bad path, session requested not found.', 404

    app.run(host=host_name, port=port_number)
