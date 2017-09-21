# i2c-001.json #
This file determines what the emulator returns on a read.

## Format ##
The key in this config is a base 10 string.  
**Beware** - The channel in the synse config is a base 16 string.(example
i2c_emulator_config-001.json).  

## Data Returned on Read ##
On the first read of a channel, the first row of data are returned.  
The emulator will then increment a counter to return the next row of data on the
next read of the same channel, **only if the read is successful.**  
The emulator will wrap the counter to the first row if there are no more.   

## Reentrancy Issues ##
Each test that reads emulator data from a channel should read all rows
from the channel. Otherwise the next test that reads from the same channel
will not begin reading from the first row.  

**Caveats:**  
- When a test fails it may not read all full rows of channel data
from the emulator.  
- This will cause the next test reading from the same channel to fail. 
- Solution is to add a reset(channel) command to signal the emulator to start
reading from the first row. Call this at the start of each test. (FUTURE)
 
# Configuration Notes #
We have multiple types of thermistors in i2c_emulator_config-001.json which
will not likely be a scenario supported in production from a physical hardware
perspective. We need it for testing only.
