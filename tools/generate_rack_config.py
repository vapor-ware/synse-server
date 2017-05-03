#!/usr/bin/env python
""" Quick utility to generate an arbitrary number of "servers" as part of generating an example rack.

    Author:  andrew
    Date:    4/8/2016

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

emuconfig = {"boards": []}

server_example = {
      "board_id": "00000001",
      "firmware_version": "OpenDCRE Emulator v1.0.0 - Standalone Server",
      "devices": [
        {
          "device_id": "0001",
          "device_type": "system",
          "asset_info": {
            "repeatable": True,
            "responses": [
              "Vapor IO,0001,Example Product,S1234567,rack mount chassis,P1234567,S1234567,A1234567,Vapor IO,P1234567,Example Product,S1234567,v1.2.0"
            ]
          },
          "boot_target": {
            "repeatable": True,
            "responses": [
              "B0",
              "B1",
              "B2"
            ]
          },
          "host_info": {
            "repeatable": True,
            "responses": [
              "i10.10.1.15,htest-server0"
            ]
          }
        },
        {
          "device_id": "0002",
          "device_type": "fan_speed",
          "read": {
            "repeatable": True,
            "responses": [
              4100,
              4100,
              4000,
              4000,
              3900,
              3900,
              3800,
              3800,
              3700,
              3700,
              3800,
              3800,
              3900,
              3900,
              4000,
              4000,
              4100,
              4100,
              4200,
              4200
            ]
          },
          "write": {
            "repeatable": True,
            "responses": [
              "W1"
            ]
          }
        },
        {
          "device_id": "0003",
          "device_type": "fan_speed",
          "read": {
            "repeatable": True,
            "responses": [
              4100,
              4100,
              4000,
              4000,
              3900,
              3900,
              3800,
              3800,
              3700,
              3700,
              3800,
              3800,
              3900,
              3900,
              4000,
              4000,
              4100,
              4100,
              4200,
              4200
            ]
          },
          "write": {
            "repeatable": True,
            "responses": [
              "W1"
            ]
          }
        },
        {
          "device_id": "0004",
          "device_type": "power",
          "power": {
            "repeatable": True,
            "responses": [
              "0,0,0,0"
            ]
          }
        },
        {
          "device_id": "0005",
          "device_type": "led",
          "read": {
            "repeatable": True,
            "responses": [
              1,
              0
            ]
          },
          "write": {
            "repeatable": True,
            "responses": [
              "W1"
            ]
          }
        },
        {
          "device_id": "2000",
          "device_type": "temperature",
          "read": {
            "repeatable": True,
            "responses": [
              28.78,
              29.77,
              30.75,
              31.84,
              32.82,
              33.81,
              34.89,
              35.88,
              36.96,
              37.94,
              38.93,
              40.21,
              41.27,
              42.33,
              43.39,
              44.45,
              45.61,
              46.57,
              47.63,
              48.69,
              49.75
            ]
          }
        },
        {
          "device_id": "4000",
          "device_type": "temperature",
          "read": {
            "repeatable": True,
            "responses": [
              28.78,
              29.77,
              30.75,
              31.84,
              32.82,
              33.81,
              34.89,
              35.88,
              36.96,
              37.94,
              38.93,
              40.21,
              41.27,
              42.33,
              43.39,
              44.45,
              45.61,
              46.57,
              47.63,
              48.69,
              49.75
            ]
          }
        }
      ]
}


for i in range(1, 61):
    # generate server
    server_example['board_id'] = "000000%0.2X" % i
    emuconfig['boards'].append(server_example.copy())
print json.dumps(emuconfig)
