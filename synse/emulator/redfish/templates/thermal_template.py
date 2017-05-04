#!/usr/bin/env python

THERMAL_TEMPLATE = {
        "@odata.context": "/redfish/v1/$metadata#Thermal.Thermal",
        "@odata.id": "/redfish/v1/Chassis/{ob_id}/Thermal",
        "@odata.type": "#Thermal.v1_0_0.Thermal",
        "Id": "Thermal",
        "Name": "Thermal Metrics",
        "Temperatures": [
            {
                "@odata.id": "/redfish/v1/Chassis/{ob_id}/Thermal#/Temperatures/1",
                "MemberId": "0",
                "Name": "CPU1 Temp",
                "SensorNumber": 42,
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                },
                "ReadingCelcius": 21,
                "UpperThresholdNonCritical": 42,
                "UpperThresholdCritical": 42,
                "UpperThresholdFatal": 42,
                "LowerThresholdNonCritical": 42,
                "LowerThresholdCritical": 5,
                "LowerThresholdFatal": 42,
                "MinimumValue": 0,
                "MaximumValue": 200,
                "PhysicalContext": "CPU",
                "RelatedItem": [
                    {"@odata.id": "/redfish/v1/Systems/437XR1138R2/Processors/CPU2" }
                ]
            },
            {
                "@odata.id": "/redfish/v1/Chassis/{ob_id}/Thermal#/Temperatures/1",
                "MemberId": "1",
                "Name": "CPU2 Temp",
                "SensorNumber": 43,
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                },
                "ReadingCelsius": 21,
                "UpperThresholdNonCritical": 42,
                "UpperThresholdCritical": 42,
                "UpperThresholdFatal": 42,
                "LowerThresholdNonCritical": 42,
                "LowerThresholdCritical": 5,
                "LowerThresholdFatal": 42,
                "MinReadingRange": 0,
                "MaxReadingRange": 200,
                "PhysicalContext": "CPU",
                "RelatedItem": [
                    {"@odata.id": "/redfish/v1/Systems/437XR1138R2/Processors/" }
                ]
            },
            {
                "@odata.id": "{rb}Chassis/{ch_id}/Thermal#/Temperatures/2",
                "MemberId": "2",
                "Name": "Chassis Intake Temp",
                "SensorNumber": 44,
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                },
                "ReadingCelsius": 25,
                "UpperThresholdNonCritical": 30,
                "UpperThresholdCritical": 40,
                "UpperThresholdFatal": 50,
                "LowerThresholdNonCritical": 10,
                "LowerThresholdCritical": 5,
                "LowerThresholdFatal": 0,
                "MinReadingRange": 0,
                "MaxReadingRange": 200,
                "PhysicalContext": "Intake",
                "RelatedItem": [
                    {"@odata.id": "{rb}Chassis/{ch_id}" },
                    {"@odata.id": "{rb}Systems/{ch_id}" }
                ]
            }
        ],
        "Fans": [
            {
                "@odata.id":"/redfish/v1/Chassis/{ob_id}/Thermal#/Fans/0",
                "MemberId":"0",
                "FanName": "BaseBoard System Fan",
                "PhysicalContext": "Backplane",
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                },
                "ReadingRPM": 2100,
                "UpperThresholdNonCritical": 42,
                "UpperThresholdCritical": 4200,
                "UpperThresholdFatal": 42,
                "LowerThresholdNonCritical": 42,
                "LowerThresholdCritical": 5,
                "LowerThresholdFatal": 42,
                "MinReadingRange": 0,
                "MaxReadingRange": 5000,
                "Redundancy" : [
                    {"@odata.id": "/redfish/v1/Chassis/{ob_id}/Thermal#/Redundancy/0"}
                ],
                "RelatedItem" : [
                    {"@odata.id": "/redfish/v1/Systems/437XR1138R2" },
                    {"@odata.id": "/redfish/v1/Chassis/{ob_id}" }
                ]
            },
            {
                "@odata.id": "/redfish/v1/Chassis/{ob_id}/Thermal#/Fans/1",
                "MemberId": "1",
                "FanName": "BaseBoard System Fan Backup",
                "PhysicalContext": "Backplane",
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                },
                 "ReadingRPM": 2100,
                "UpperThresholdNonCritical": 42,
                "UpperThresholdCritical": 4200,
                "UpperThresholdFatal": 42,
                "LowerThresholdNonCritical": 42,
                "LowerThresholdCritical": 5,
                "LowerThresholdFatal": 42,
                "MinReadingRange": 0,
                "MaxReadingRange": 5000,
                "Redundancy" : [
                    {"@odata.id": "/redfish/v1/Chassis/{ch_id}/Power#/Redundancy/0"}
                ],
                "RelatedItem" : [
                    {"@odata.id": "/redfish/v1/Systems/437XR1138R2" },
                    {"@odata.id": "/redfish/v1/Chassis/{ob_id}" }
                ]
            }
        ],
        "Redundancy": [
            {
                "@odata.id": "/redfish/v1/Chassis/{ob_id}/Thermal#/Redundancy/0",
                "MemberId": "0",
                "Name": "BaseBoard System Fans",
                "RedundancySet": [
                    { "@odata.id": "/redfish/v1/Chassis/{ob_id}/Thermal#/Fans/0" },
                    { "@odata.id": "/redfish/v1/Chassis/{ob_id}/Thermal#/Fans/1" }
                ],
                "Mode": "N+1",
                "Status": {
                    "State": "Enabled",
                    "Health": "OK"
                },
                "MinNumNeeded": 1,
                "MaxNumSupported": 2
            }
        ]
    }