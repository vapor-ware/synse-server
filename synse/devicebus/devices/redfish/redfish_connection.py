#!/usr/bin/env python
""" Redfish Connection Methods for Synse Redfish Bridge.

NOTE (v1.3): Redfish is still in Beta and is untested on live hardware.


    Author:  Morgan Morley Mills
    Date:    01/12/2017

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

import logging

import requests
from requests.auth import HTTPBasicAuth

from synse.errors import SynseException

logger = logging.getLogger(__name__)


def _build_link(ip_address, port, path, timeout=None):
    """ Builds a new link based upon the arguments passed in to query the Redfish server.

    Args:
        ip_address (str): the ip_address of the Redfish server.
        port (str | int): the port of the Redfish server.
        path (str): the location of the link within the Redfish server. if this is the
            root link, the path specified should be 'root'.
        timeout (int | float): the number of seconds a GET will wait for a connection
            before timing out on the request. this parameter is not None only when
            attempting to find the root path.

    Returns:
        str: the URI of the link specified by the args.
    """
    _link = 'http://' + str(ip_address) + ':' + str(port)
    if path == 'root' and timeout is not None:
        get_root_path = get_data(link=_link + '/redfish', timeout=timeout)
        get_root_path = str(get_root_path.values()[0]).rstrip('/')
        _link += get_root_path
    elif path != 'root' and path is not None:
        _link += path

    if '/redfish' in _link:
        return _link
    else:
        logger.error('Bad path to build a link: {}.'.format(path))
        raise ValueError('Cannot build link for {} path. Bad link: {}.'.format(path, _link))


def get_data(link, timeout, username=None, password=None):
    """ Gets the JSON data from the Redfish server via the link specified.

    Args:
        link (str): the link to which information is requested.
        timeout (int | float): the number of seconds a GET will wait for a connection
            before timing out on the request.
        username (str): the username for basic authentication.
        password (str): the password for basic authentication.

    Returns:
        dict: a representation of the JSON data from the Redfish server.
    """
    try:
        if username is not None and password is not None:
            r = requests.get(link, timeout=timeout, auth=HTTPBasicAuth(username, password))
        else:
            r = requests.get(link, timeout=timeout)
    except requests.exceptions.ConnectionError as e:
        raise SynseException('Unable to GET link {} due to ConnectionError: {}'.format(link, e.message))

    if r.status_code != 200:
        logger.error('Unexpected status code for GET method: {}'.format(r.status_code))
        raise ValueError('Unable to GET link {}. Status code: {}'.format(link, r.status_code))
    else:
        return r.json()


def patch_data(link, payload, timeout, username, password):
    """ Patches JSON data from the Redfish server via the link specified.

    Args:
        link (str): the link to which information is requested.
        payload (dict): the data to patch.
        timeout (int | float): the number of seconds a PATCH will wait for a
            connection before timing out on the request.
        username (str): the username for basic authentication.
        password (str): the password for basic authentication.
    """
    r = requests.patch(link, json=payload, timeout=timeout, auth=HTTPBasicAuth(username, password))
    if r.status_code != 200:
        logger.error('Unexpected status code for PATCH method: {}'.format(r.status_code))
        raise ValueError('Unable to PATCH link {}. Status code: {}'.format(link, r.status_code))


def post_action(link, payload, timeout, username, password):
    """ Posts an action from to the Redfish server via the link specified.

    Args:
        link (str): the link to which data is requested.
        payload (dict): the data to POST.
        timeout (int | float): the number of seconds a POST will wait for a
            connection before timing out on the request.
        username (str): the username for basic authentication.
        password (str): the password for basic authentication.
    """
    r = requests.post(link, json=payload, timeout=timeout, auth=HTTPBasicAuth(username, password))
    if r.status_code != 200:
        logger.error('Unexpected status code for POST method: {}'.format(r.status_code))
        raise ValueError('Unable to POST link {}. Status code: {}'.format(link, r.status_code))


# Traversing the tree:


def _get_members(json_data, ip_address, port):
    """ Get all the members from the collection data on a Redfish device.

    Args:
        json_data (dict): the data too be searched through for a Member collection.
        ip_address (str): the ip_address of the Redfish server.
        port (str | int): the port of the Redfish server.

    Returns:
        list[str]: all the links from the members collection.
    """
    members_list = list()
    if 'Members' in json_data:
        try:
            if int(json_data['Members@odata.count']) == 1:
                return [_build_link(ip_address=ip_address, port=port, path=str(json_data['Members'][0]['@odata.id']))]
            else:
                for item in json_data['Members']:
                    members_list.append(_build_link(ip_address=ip_address, port=port, path=str(item['@odata.id'])))
                return members_list
        except KeyError as e:
            logger.error('Collection defined without {}.'.format(e.message))
            raise SynseException('Unable to verify number of members. {} not present.'.format(e.message))
    else:
        logger.error('No Members collection defined in {} schema.'.format(json_data['Name']))
        raise ValueError('Cannot find Members collection in the data specified: {}'.format(json_data['Name']))


def _get_inner_link(col, search_word, ip_address, port):
    """ Searches the various levels returned data may be in to find a link either
    whose key is the search_word, or whose URI contains a specific word which is
    the search_word.

    Args:
        col (dict | list): the collection to sort through, whether a list of URIs or
            all the data from a schema.
        search_word (str): the key to search for within the schema or a word within
            a URI from members list generated by _get_all_members().
        ip_address (str): the ip_address of the Redfish server.
        port (str | int): the port of the Redfish server.

    Returns:
        str: the link that corresponds to the search_word specified.
    """
    if isinstance(col, dict):
        if search_word in col:
            if '@odata.id' in col[search_word]:
                return _build_link(ip_address=ip_address, port=port, path=str(col[search_word]['@odata.id']))
        if 'Members' in col:
            return _get_inner_link(col=_get_members(json_data=col, ip_address=ip_address, port=port),
                                   search_word=search_word,
                                   ip_address=ip_address,
                                   port=port)
    elif isinstance(col, list):
        for member in col:
            if search_word in member:
                return member
    # if it hits this, it has not found the search word in the collection.
    logger.error('{} is not a term found in the collection.'.format(search_word))
    raise ValueError('Cannot find the {} in the data specified.'.format(search_word))


def find_links(ip_address, port, timeout, username, password):
    """ Find links to schemas on the remote system for scans or initialization.

    Args:
        ip_address (str): the ip address of the Redfish server.
        port (str | int): the port for the Redfish server.
        timeout (int | float): the number of seconds a GET will wait for a connection
            before timing out on the request.
        username (str): the username for basic HTTP authentication.
        password (str): the password for basic HTTP authentication.

    Returns:
        dict: key: label of remote schema, value: corresponding URIs to schemas on
            the remote system.
    """
    collections = dict()
    response = dict()

    try:
        root = _build_link(ip_address=ip_address, port=port, path='root', timeout=timeout)
        root_data = get_data(root, timeout=timeout)

        collections['managers'] = get_data(
            link=_build_link(ip_address=ip_address, port=port, path=root_data['Managers']['@odata.id']),
            timeout=timeout,
            username=username,
            password=password
        )
        collections['systems'] = get_data(
            link=_build_link(ip_address=ip_address, port=port, path=root_data['Systems']['@odata.id']),
            timeout=timeout,
            username=username,
            password=password
        )
        collections['chassis'] = get_data(
            link=_build_link(ip_address=ip_address, port=port, path=root_data['Chassis']['@odata.id']),
            timeout=timeout,
            username=username,
            password=password
        )
    except ValueError as e:
        expected_keys = ['managers', 'chassis', 'systems']
        unfound = ', '.join(set(expected_keys).difference(collections.keys()))
        logger.error('{} collection(s) unable to be retrieved with current information: {}'.format(unfound, e.message))
        raise SynseException('Cannot retrieve {} collection links from root schema: {}.'.format(unfound, e.message))

    try:
        response['bmc'] = _get_members(
            json_data=collections['managers'],
            ip_address=ip_address,
            port=port
        )[0]
        # TODO - for later development of remote devices with multiple systems running on the same ip, add a config
        #   value with system names. If there are more than one system in the members list, the search_word
        #   specified should be replaced with the name of the desired system. Otherwise, this function will
        #   always return the first of the members.
        response['system'] = _get_inner_link(
            col=collections['systems'],
            search_word='Systems',
            ip_address=ip_address,
            port=port
        )

        response['chassis'] = _get_members(
            json_data=collections['chassis'],
            ip_address=ip_address,
            port=port
        )[0]

        chassis_data = get_data(link=response['chassis'], timeout=timeout, username=username, password=password)
        response['thermal'] = _get_inner_link(chassis_data, search_word='Thermal', ip_address=ip_address, port=port)
        response['power'] = _get_inner_link(chassis_data, search_word='Power', ip_address=ip_address, port=port)
        return response
    except KeyError as e:
        expected_keys = ['bmc', 'system', 'chassis', 'thermal', 'power']
        unfound = ', '.join(set(expected_keys).difference(response.keys()))
        logger.error('Cannot retrieve {} links. Bad path to {}.'.format(unfound, e.message))
        raise SynseException('Cannot retrieve links from collections: {}. Bad path to {}.'.format(unfound, e.message))
