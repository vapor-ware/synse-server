# IPMI Emulator Data

This directory contains files which are loaded into the emulator on startup to define the data that it will serve.
There are various different files which are expected. All of which need to be accounted for when configuring the
emulator to run.

## Data Files

### sdr.json

A JSON document which describes the BMC's SDR record. Below is an example of a valid SDR JSON config. All the
fields below are required for a valid SDR configuration.

```json
{
  "sdr_version": 1.5,
  "record_count": 21,
  "free_space": 1663,
  "latest_addition_ts": 0,
  "latest_erase_ts": 0,
  "operation_support": "2f"
}
```

where

<dl>
  <dt>sdr_version</dt>
  <dd>the version of the sdr. to be encoded into a single byte, e.g. 1.5 -> 0x51</dd>

  <dt>record count</dt>
  <dd>the number of records in the sdr (this should correspond to the sdr record definition count). to be encoded
  as two bytes with padding if necessary</dd>
  
  <dt>free_space</dt>
  <dd>the free space left on the sdr - not overly important for the emulator but necessary to create the record</dd>
  
  <dt>latest_addition_ts</dt>
  <dd>time in seconds since SEL device's initialization (is fine to leave as 0)</dd>
  
  <dt>latest_erase_ts</dt>
  <dd>time in seconds since SEL device's initialization (is fine to leave as 0)</dd>
  
  <dt>operation_support</dt>
  <dd>byte encoding the operations supported by the sdr (see snippet below for example)</dd>
</dl>

**example of operation_support encoding (taken from wireshark)**
```
0... .... = Overflow: False
.01. .... = SDR Repository Update: Supported non-modal (0x01)
.... 1... = Delete SDR: True
.... .1.. = Partial Add SDR: True
.... ..1. = Reserve SDR Repository: True
.... ...1 = Get SDR Repository Allocation Info: True
```
*it is left up to the configurer to set the correct byte here to their liking*


### bmc.json

A JSON document which describes a BMC's starting state. Note that these configurations are only
loaded into memory on emulator initialization. Afterwords, any modifications to the emulated BMC
must be done through IPMI commands.

Below is an example of a valid BMC JSON config. All the fields below are required for a valid BMC 
configuration.

```json
{
  "device": {
    "device_id": "20",
    "device_revision": "01",
    "device_availability": "03",
    "minor_firmware_revision": "16",
    "ipmi_version": "02",
    "additional_device_support": "bf",
    "manufacturer_id": 47488,
    "product_id": 2566
  },
  "chassis": {
    "current_power_state": "01",
    "last_power_event": "00",
    "misc_state": "40"
  },
  "channel_auth_capabilities": {
    "channel": "01",
    "version_compatibility": "16",
    "user_capabilities": "06",
    "supported_connections": "00",
    "oem_id": 21317,
    "oem_auxiliary_data": "00"
  }
}
```

where

<dl>
  <dt>device</dt>
  <dd>an object which contains the fields needed for the 'get device id' operation. this can either be
  specified as an object (as seen in the example, above) or as a list of bytes.
  
  <dl>
    <dt>device_id</dt>
    <dd>the id of the device (provided as a hexadecimal string)</dd>
    
    <dt>device_revision</dt>
    <dd>the revision of the device (provided as a hexadecimal string)</dd>
    
    <dt>device_availability</dt>
    <dd>availability of the device (provided as a hexadecimal string)</dd>
    
    <dt>minor_firmware_revision</dt>
    <dd>device minor firmware revision (provided as a hexadecimal string)</dd>
    
    <dt>ipmi_version</dt>
    <dd>ipmi version supported by the device (provided as a hexadecimal string)</dd>
    
    <dt>additional_device_support</dt>
    <dd>devices supported by the bmc - for the bit map, see below. (provided as a hexadecimal string)</dd>
    
    <dt>manufacturer_id</dt>
    <dd>the id of the bmc manufacturer (3 bytes, encoded at runtime)</dd>
    
    <dt>product_id</dt>
    <dd>the product id (2 bytes, encoded at runtime)</dd>
  </dl>  
  </dd>
  
  <dt>chassis</dt>
  <dd>an object which contains the fields needed to define chassis information used by various commands,
  such as chassis identify and getting chassis status.
  
  <dl>    
    <dt>current_power_state</dt>
    <dd></dd>
    
    <dt>last_power_event</dt>
    <dd></dd>
    
    <dt>misc_state</dt>
    <dd></dd>
  </dl>
  </dd>
  
  <dt>channel_auth_capabilities</dt>
  <dd>an object which contains the fields needed for the 'get channel authentication capabilities request.
  
  <dl>
    <dt>channel</dt>
    <dd></dd>
    
    <dt>version_compatibility</dt>
    <dd></dd>
    
    <dt>user_capabilities</dt>
    <dd></dd>
    
    <dt>supported_connections</dt>
    <dd></dd>
    
    <dt>oem_id</dt>
    <dd></dd>
    
    <dt>oem_auxiliary_data</dt>
    <dd></dd>
  </dl>
  </dd>
</dl>

#### bit maps
***device.additional_device_support***
```

```

***chassis.current_power_state***
```
.00. .... = Power Restore Policy: chassis stays powered off after AC returns (0x00)
...0 .... = Power Control Fault: False
.... 0... = Power Fault: False
.... .0.. = Interlock: False
.... ..0. = Overload: False
.... ...1 = Power is on: True
```

***chassis.last_power_event***
```
...0 .... = Last 'Power is on' state was entered via IPMI command: False
.... 0... = Last power down caused by power fault: False
.... .0.. = Last power down caused by a power interlock being activated: False
.... ..0. = Last power down caused by a power overload: False
.... ...0 = AC failed: False
```

***chassis.misc_state***
```
.1.. .... = Chassis identify command and state info supported: True
..00 .... = Chassis identify state (if supported): Off (0x00)
.... 0... = Cooling/fan fault detected: False
.... .0.. = Drive loss: False
.... ..0. = Front Panel Lockout active: False
.... ...0 = Chassis Intrusion active: False
```

### sdr_entries.json

*Note:* The "sensor type" field is not used internally, but is used to identify the sensor
to anyone reading or modifying the record. The name information is encoded at the end of the 
'data' list, so can also be determined from that.