# Emulator for SNMP

Spin up the emulator by:
```
make snmp-yml
```

The file in data/public.snmprec is used by the snmp emulator to server OIDs from the Rittal MIB for reads.
data/private.snmprec is read/write if the specific OID is setup that way in the file. For more information
see: http://snmpsim.sourceforge.net/simulation-with-variation-modules.html#writecache

To generate the data file:
Download the Rittal MIB from here: http://www.rittal.de/downloads/rimatrix5/software/RiZoneMib_v3.6.zip
Unzip it.
Rename it to RITTAL-RIZONE-MIB.txt (Not clear if this copy is needed.)
```
cp RITTAL-RIZONE-MIB.txt /usr/share/snmp/mibs/
pip install pysmi
pip install snmpsim
python /usr/local/bin/mibdump.py RITTAL-RIZONE-MIB.txt
mkdir rawdata
mib2dev.py --mib-module=RITTAL-RIZONE-MIB > rawdata/RITTAL-RIZONE-MIB.snmprec
mib2dev.py --mib-module=SNMPv2-MIB > rawdata/SNMPv2-MIB.snmprec
mkdir data
cat rawdata/RITTAL-RIZONE-MIB.snmprec rawdata/SNMPv2-MIB.snmprec > data/public.snmprec
cp public.snmprec private.snmprec
# Then edit private.snmprec to make specific OIDs writable (see above writecache link)
```

The python-mibs directory is the output of the mibdump.py command.

# How to create a test MIB

Copy an existing test MIB and start from that.

Make sure that the enterprise number is not another organization's.
We don’t have an IANA enterprise number 
    (see https://www.iana.org/assignments/enterprise-numbers/enterprise-numbers)
Chose 61439 which is 0xEFFF

Write it up how you like.
Tutorials and references:
http://net-snmp.sourceforge.net/wiki/index.php/Writing_your_own_MIBs
