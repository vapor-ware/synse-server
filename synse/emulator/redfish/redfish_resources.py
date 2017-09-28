#!/usr/bin/env python
""" Resource handler

Functions called on emulator startup to walk through mockup file tree
and populate a dictionary database with paths to resources as keys and
content of the resource index.json file as values. Stores username and
passwords found in mockup's AccountService/Accounts in dictionary for
basic auth.

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

import json
import os

database = {}

# users dictionary for HTTPbasicauth based on existing accounts in AccountServices
# mockup file in addition to hardcoded username and password
users = {'root': 'redfish'}


def get_all_resources(mockup_name):
    """ Get all resources for the specified Redfish mockup.
    """
    root_dir_path = os.path.normpath('./Resources/{}'.format(mockup_name))
    try:
        for dir_name, _, file_list in os.walk(root_dir_path):
            for file_name in file_list:
                if file_name != 'index.json':
                    continue
                else:
                    path = os.path.join(dir_name, file_name)
                    with open(path, 'r') as f:
                        database[dir_name] = json.load(f)
        register_users(mockup_name)
        return database
    except OSError:
        return 'Mockup name specified in not in Resource directory.'


def register_users(mockup_name):
    """ Get a mapping of users in the Redfish mockup.
    """
    root_dir_path = os.path.normpath(
        './Resources/{}/redfish/v1/AccountService/Accounts'.format(mockup_name))
    for name in os.listdir(root_dir_path):
        if name not in ['index.json', 'root']:
            database_key = os.path.join(root_dir_path, name)
            users[name] = database[database_key]['Password']
        else:
            pass
    return users
