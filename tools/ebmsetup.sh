#!/usr/bin/env bash

# Read the defaults
sudo python ebmfan.py get all


# Setup each register.
#    0xD000: 'Reset',
#    # Appears to be the speed setting.
#    0xD001: 'Set Value',
#    0xD002: 'Password',
#    0xD003: 'Password',
#    0xD004: 'Password',
#    0xD005: 'Factory Setting Control',  # Restore factory defaults or set what the defaults are.
#    0xD006: 'Customer Setting Control',
#
#    0xD009: 'Operating Hours Counter',
#    0xD00A: 'Operating Minutes Counter',
#    0xD00C: 'Addressing On/Off',  # Won't likely need.
#    0xD00D: 'Stored Set Value (parameter set 1)',
#    0xD00E: 'Stored Set Value (parameter set 2)',
#    0xD00F: 'Enable / Disable',
#    0xD010: 'Remote Control Output 0-10 V',
#
#    0xD100: 'Fan Address',
#    # Needs to be 1, RS485.
#    0xD101: 'Set Value Source',
#    # Needs to be either 0 (counterclockwise) or 1 (clockwise). Try 0 first.
#    0xD102: 'Preferred Running Direction',
#    # Default here appears to be 1, Set value and Enable / Disable are stored. Seems fine at 1.
#    0xD103: 'Store Set Value',
#    # Appears we need 1, Parameter "Parameter Set Internal."
#    0xD104: 'Switch for Parameter Set Source',
sudo python ebmfan.py set register D104 1

#    # Default unclear (likely 0). Set to 0 for parameter set 1.
#    0xD105: 'Parameter Set Internal',
#    # Default here appears to be 2, Open Loop PWM control which is what we want.
#    0xD106: 'Operating Mode (parameter set 1)',
#    # Default here appears to be 2, Open Loop PWM control which is what we want.
#    0xD107: 'Operating Mode (parameter set 2)',
#    # Default here appears to be 0, positive / heating. Shouldn't matter for open loop.
#    0xD108: 'Controller function (parameter set 1)',
#    # Default here appears to be 0, positive / heating. Shouldn't matter for open loop.
#    0xD109: 'Controller function (parameter set 2)',
#    # Setting the four control parameters to zero should disable control. Set this to 0.
#    0xD10A: 'P factor (parameter set 1)',
sudo python ebmfan.py set register D10A 0
#    # Setting the four control parameters to zero should disable control. Set this to 0.
#    0xD10B: 'P factor (parameter set 2)',
sudo python ebmfan.py set register D10B 0
#    # Setting the four control parameters to zero should disable control. Set this to 0.
#    0xD10C: 'I factor (parameter set 1)',
sudo python ebmfan.py set register D10C 0
#    # Setting the four control parameters to zero should disable control. Set this to 0.
#    0xD10D: 'I factor (parameter set 2)',
sudo python ebmfan.py set register D10D 0
#    # Default here appears to be 256d 0x100, which means 100% and is what we want.
#    0xD10E: 'Max Modulation Level (parameter set 1)',
#    # Default here appears to be 256d 0x100, which means 100% and is what we want.
#    0xD10F: 'Max Modulation Level (parameter set 2)',
#
#    # Default here appears to be 13d 0xD, which means 5%. We want 10%. Set to 26d 0x1A. (5% may be fine. see D118)
#    0xD110: 'Min Modulation Level (parameter set 1)',
sudo python ebmfan.py set register D110 1A
#    # Default here appears to be 13d 0xD, which means 5%. We want 10%. Set to 26d 0x1A. (5% may be fine. see D119)
#    0xD111: 'Min Modulation Level (parameter set 2)',
sudo python ebmfan.py set register D111 1A
#    # Should be 1 here. Motor stops when set value = 0.
#    0xD112: 'Motor Stop Enable (parameter set 1)',
sudo python ebmfan.py set register D112 1
#    # Should be 1 here. Motor stops when set value = 0.
#    0xD113: 'Motor Stop Enable (parameter set 2)',
sudo python ebmfan.py set register D113 1
#
#    # Believe this should be 0.
#    0xD116: 'Starting Modulation Level',
sudo python ebmfan.py set register D116 0
#    # Believe this should be 256 0x100 for max modulation of 100%.
#    0xD117: 'Max Permissible Modulation Level',
sudo python ebmfan.py set register D117 100
#    # Believe this should be 26 0x1A for min modulation of 10%.
#    0xD118: 'Min Permissible Modulation Level',
sudo python ebmfan.py set register D118 26

#    # Pretty sure we want 1110 decimal, 0x456 (rpm) here.
#    0xD119: 'Maximum Speed',
sudo python ebmfan.py set register D119 456
#    # Pretty sure we want 1110 decimal, 0x456 (rpm) here.
#    0xD11A: 'Maximum Permissible Speed',
sudo python ebmfan.py set register D11A 456

#    # TODO: Should look at this more.
#    # TODO: Zero may be bad here. Check default. Try 1 = 2.5 seconds.
#    0xD11F: 'Ramp-Up Time',
sudo python ebmfan.py set register D11F 1

#    # TODO: Should look at this more.
#    # TODO: Zero may be bad here. Check default. Try 1 = 2.5 seconds.
#    0xD120: 'Ramp-Down Time',
sudo python ebmfan.py set register D120 1

#    # TODO:
#    # Pretty sure we want 1110 decimal, 0x456 (rpm) here.
#    0xD128: 'Speed Limit',
sudo python ebmfan.py set register D128 456

#    # TODO: Should look at this more.
#    0xD12A: 'Input char. curve point 1 X-coordinate (par. 1)',
#    0xD12B: 'Input char. curve point 1 Y-coordinate (par. 1)',
#    0xD12C: 'Input char. curve point 2 X-coordinate (par. 1)',
#    0xD12D: 'Input char. curve point 2 Y-coordinate (par. 1)',
#    # TODO: Check this out. Think this should be 1, "Controller Function", but it may not matter.
sudo python ebmfan.py set register D12D 1

#    0xD12E: 'Source for Controller Function',
#    # Believe the default will be zero which is fine.
#    0xD12F: 'Limitation Control',
#
#    # TODO: Should look at this more.
#    # Check the default.
#    # Believe we want 1 for the LSB, Actual Speed.
#    # MSB looks like encoder pulses per revolution, but this is an output ...
#    0xD130: 'Function output 0..10 V / speed monitoring',
sudo python ebmfan.py set register D130 1

#    # TODO: Should look at this more.
#    # This is part of the power limiter.
#    0xD135: 'Maximum Permissible Power',
#    # TODO: Should look at this more.
#    # These three are part of the power limiter.
#    0xD136: 'Max Power at derating end.',
#    0xD137: 'Module temperature power derating start',
#    0xD138: 'Module temperature power derating end',
#
#    # TODO: Should look at this more.
#    # Part of Limitation Control.
#    0xD13B: 'Maximum Winding Current',
#    0xD13C: 'Input char. curve point 1 X-coordinate (par. 2)',
#    0xD13D: 'Input char. curve point 1 Y-coordinate (par. 2)',
#    0xD13E: 'Input char. curve point 2 X-coordinate (par. 2)',
#    0xD13F: 'Input char. curve point 2 Y-coordinate (par. 2)',
#
#    # TODO: Should look at this more.
#    # TODO: Map of voltage to output.
#    0xD140: 'Char. curve output 0..10 V point 1 X',
#    0xD141: 'Char. curve output 0..10 V point 1 Y',
#    0xD142: 'Char. curve output 0..10 V point 2 X',
#    0xD143: 'Char. curve output 0..10 V point 2 Y',
#
#    # TODO: Should look at this more.
#    # It looks like we want this set to 0xFA00, which is the same as max rpm by formula.
#    0xD145: 'Run Monitoring Speed Limit',
#
#    # TODO: Should look at this more.
#    # Not clear that this matters.
#    0xD147: 'Sensor Actual Value Source',
#    # Needs to be 1, Parameter "Preferred Running Direction Only."
#    0xD148: 'Switch for Rotating Direction Source',
sudo python ebmfan.py set register D148 1
#
#    # TODO: Baud Rate. Should default to 19200 which is a setting of 4.
#    0xD149: 'Communication Speed',
#
#    # TODO: Parity. Should default to even which is what we want. (Setting 0.)
#    0xD14A: 'Parity Configuration',
#
#    # TODO: Should look at this more.
#    # These two are part of the power limiter.
#    0xD14D: 'Motor temperature power derating start',
#    0xD14E: 'Motor temperature power derating end',
#
#    # TODO: Should look at this more.
#    # Shedding function is run to attempt to shake the fan free when stuck.
#    0xD150: 'Shedding Function',
#    0xD151: 'Max Start PWM Shedding',
#    0xD152: 'Max Number of Start Attempts',
#    0xD153: 'Relay Drop-out Delay',
#
#    # TODO: Should look at this more.
#    # This is part of the power limiter.
#    0xD155: 'Maximum Power',
#
#    0xD158: 'Configuration I/O 1',
#    0xD159: 'Configuration I/O 2',
     # TODO: Needs to be Analog output to get the rpm. See 2.37 and 2.45.
#    0xD15A: 'Configuration I/O 3',
sudo python ebmfan.py set register D15A 4
#
#    # TODO: This should be 0x2, set direction maintained.
#    0xD15B: 'Rotating Direction Fail-Safe Mode',
#
sudo python ebmfan.py set register D15B 2
#    # TODO:
#    # Looks like this should be 1, Failsafe function set value specified by
#    # parameter set value for failsafe function.
#    0xD15C: 'Fail-Safe Set Value Source',
sudo python ebmfan.py set register D15C 1

#    # TODO:
#    # This should be 0xFA00 (64000d) to run the fan full speed on failure.
#    0xD15D: 'Set Value Fail-Safe Speed',
sudo python ebmfan.py set register D15C FA00

#
#    # TODO:
#    # This should be 0x258 to run the fan at the failsafe speed after one minute.
#    0xD15E: 'Time Lag Fail-Safe Speed',
sudo python ebmfan.py set register D15C 258

#    # Looks like we don't need this. Not setting by analog input.
#    0xD15F: 'Cable Break Detection Voltage',
#
#    # Looks like we don't need this. Not controlling by sensor.
#    0xD160: 'Minimum Sensor Value',
#    0xD161: 'Minimum Sensor Value',
#    0xD162: 'Maximum Sensor Value',
#    0xD163: 'Maximum Sensor Value',
#    0xD164: 'Sensor Unit',
#    0xD165: 'Sensor Unit',
#    0xD166: 'Sensor Unit',
#    0xD167: 'Sensor Unit',
#    0xD168: 'Sensor Unit',
#    0xD169: 'Sensor Unit',
#    # Check default. 0 is inactive, 1 is parameter.
#    # TODO: Should likely be 1, "Parameter Enable / Disable.
#    0xD16A: 'Switch for Enable / Disable Source',
sudo python ebmfan.py set register D15A 1

#    # TODO: Should likely be 1, Enable.
#    0xD16B: 'Stored Enable / Disable',
sudo python ebmfan.py set register D15B 1

#    # Needs to be 0, Parameter Set Value Source.
#    0xD16C: 'Switch for Set Value Source',

#    # TODO: Should look at this more.
#    # Part of the power limiter.
#    0xD16D: 'Power Derating Ramp',
#    0xD16E: 'Voltage Output',
#    # Sould be zero. Access to parameter via RFID interface not permitted
#    0xD16F: 'RFID Access',
#
#    0xD170: 'Customer Data',
#    0xD171: 'Customer Data',
#    0xD172: 'Customer Data',
#    0xD173: 'Customer Data',
#    0xD174: 'Customer Data',
#    0xD175: 'Customer Data',
#    0xD176: 'Customer Data',
#    0xD177: 'Customer Data',
#    0xD178: 'Customer Data',
#    0xD179: 'Customer Data',
#    0xD17A: 'Customer Data',
#    0xD17B: 'Customer Data',
#    0xD17C: 'Customer Data',
#    0xD17D: 'Customer Data',
#    0xD17E: 'Customer Data',
#    0xD17F: 'Customer Data',
#
#    0xD180: 'Operating Hours Counter (backup)',
#
#    0xD182: 'Error Indicator',
#
#    0xD184: 'First Error',
#    0xD185: 'Time of First Error',
#    0xD186: 'Error History / Time',
#    0xD187: 'Error History / Time',
#    0xD188: 'Error History / Time',
#    0xD189: 'Error History / Time',
#    0xD18A: 'Error History / Time',
#    0xD18B: 'Error History / Time',
#    0xD18C: 'Error History / Time',
#    0xD18D: 'Error History / Time',
#    0xD18E: 'Error History / Time',
#    0xD18F: 'Error History / Time',
#
#    0xD190: 'Error History / Time',
#    0xD191: 'Error History / Time',
#    0xD192: 'Error History / Time',
#    0xD193: 'Error History / Time',
#    0xD194: 'Error History / Time',
#    0xD195: 'Error History / Time',
#    0xD196: 'Error History / Time',
#    0xD197: 'Error History / Time',
#    0xD198: 'Error History / Time',
#    0xD199: 'Error History / Time',
#    0xD19A: 'Error History / Time',
#    0xD19B: 'Error History / Time',
#    0xD19C: 'Error History / Time',
#    0xD19D: 'Error History / Time',
#    0xD19E: 'Error History / Time',
#    0xD19F: 'Error History / Time',
#
#    # TODO: Should look at this more. Check with Steve.
     # Nominal Volatage is 400V. Range is  380V-480V
     # Setting is in 20 mV increments, so 50d is 1V.
     # For 400V, setting is 20000d 0x4E20
#    0xD1A0: 'DC-Link Voltage Reference Value',
sudo python ebmfan.py set register D1A0 4E20

#    # TODO: Should look at this more.
     # Current Draw is 4.35A.
     # Setting is in 2 mA increments, so 500d is 1A
     # For 4.35A, setting is 2175d 0x87F
#    0xD1A1: 'DC-Link Current Reference Value',
sudo python ebmfan.py set register D1A0 87F

#    0xD1A2: 'Fan Serial Number',
#    0xD1A3: 'Fan Serial Number',
#    0xD1A4: 'Date of Fan Manufacture',
#    0xD1A5: 'Fan Type',
#    0xD1A6: 'Fan Type',
#    0xD1A7: 'Fan Type',
#    0xD1A8: 'Fan Type',
#    0xD1A9: 'Fan Type',
#    0xD1AA: 'Fan Type',
#
#    0xD1F7: 'Rotor position sensor calibration set value',
#    0xD1F8: 'Rotor position sensor calibration',

# Reset to transfer parameters from EEPROM to RAM.
sudo python ebmfan.py set register D000 2