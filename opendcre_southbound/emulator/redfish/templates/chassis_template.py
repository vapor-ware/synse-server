#!/usr/bin/env python


CHASSIS_TEMPLATE = {
        "@odata.context": "/redfish/v1/$metadata#Chassis.Chassis",
        "@odata.id": "/redfish/v1/Chassis/{id}",
        "@odata.type": "#Chassis.v1_0_0.Chassis",
        "Id": "{id}",
        "Name": "Computer System Chassis",
        "ChassisType": "RackMount",
        "Manufacturer": "Redfish Computers",
        "Model": "3500RX",
        "SKU": "8675309",
        "SerialNumber": "437XR1138R2",
        "Version": "1.02",
        "PartNumber": "224071-J23",
        "AssetTag": "Chicago-45Z-2381",
        "Status": {
            "State": "Enabled",
            "Health": "OK"
        },
        "Thermal": {
            "@odata.id": "/redfish/v1/Chassis/{id}/Thermal"
        },
        "Power": {
            "@odata.id": "/redfish/v1/Chassis/{id}/Power"
        },
        "Links": {
            "ComputerSystems": [
                {
                    "@odata.id": "/redfish/v1/Systems/"
                }
            ],
            "ManagedBy": [
                {
                    "@odata.id": "/redfish/v1/Managers/"
                }
            ],
         },
    }
