"""
PySNMP MIB module TEST-MIB1 (http://pysnmp.sf.net)
ASN.1 source file:///usr/share/snmp/mibs/TEST-MIB1.txt
Produced by pysmi-0.0.7 at Thu Feb  2 10:21:59 2017
On host elektrode platform Darwin version 16.4.0 by user mhink
Using Python version 2.7.10 (default, Jul 30 2016, 19:40:32)

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
( Integer, ObjectIdentifier, OctetString, ) = mibBuilder.importSymbols("ASN1", "Integer", "ObjectIdentifier", "OctetString")
( NamedValues, ) = mibBuilder.importSymbols("ASN1-ENUMERATION", "NamedValues")
( ConstraintsUnion, SingleValueConstraint, ConstraintsIntersection, ValueSizeConstraint, ValueRangeConstraint, ) = mibBuilder.importSymbols("ASN1-REFINEMENT", "ConstraintsUnion", "SingleValueConstraint", "ConstraintsIntersection", "ValueSizeConstraint", "ValueRangeConstraint")
( NotificationGroup, ModuleCompliance, ) = mibBuilder.importSymbols("SNMPv2-CONF", "NotificationGroup", "ModuleCompliance")
( sysName, sysLocation, sysContact, ) = mibBuilder.importSymbols("SNMPv2-MIB", "sysName", "sysLocation", "sysContact")
( Integer32, MibScalar, MibTable, MibTableRow, MibTableColumn, NotificationType, MibIdentifier, IpAddress, TimeTicks, Counter64, Unsigned32, enterprises, iso, Gauge32, ModuleIdentity, ObjectIdentity, Bits, Counter32, ) = mibBuilder.importSymbols("SNMPv2-SMI", "Integer32", "MibScalar", "MibTable", "MibTableRow", "MibTableColumn", "NotificationType", "MibIdentifier", "IpAddress", "TimeTicks", "Counter64", "Unsigned32", "enterprises", "iso", "Gauge32", "ModuleIdentity", "ObjectIdentity", "Bits", "Counter32")
( DisplayString, TextualConvention, ) = mibBuilder.importSymbols("SNMPv2-TC", "DisplayString", "TextualConvention")
testEnterprise = MibIdentifier((1, 3, 6, 1, 4, 1, 61439))
testDevice1 = MibIdentifier((1, 3, 6, 1, 4, 1, 61439, 1))
testDevice1Rev = MibIdentifier((1, 3, 6, 1, 4, 1, 61439, 1, 1))
testDevice1Status = MibIdentifier((1, 3, 6, 1, 4, 1, 61439, 1, 4))
testDevice1Power = MibIdentifier((1, 3, 6, 1, 4, 1, 61439, 1, 4, 1))
testDevice1Fan = MibIdentifier((1, 3, 6, 1, 4, 1, 61439, 1, 4, 2))
testDevice1Led = MibIdentifier((1, 3, 6, 1, 4, 1, 61439, 1, 4, 3))
testDevice1RevMajor = MibScalar((1, 3, 6, 1, 4, 1, 61439, 1, 1, 1), Integer32()).setMaxAccess("readonly")
testDevice1RevMinor = MibScalar((1, 3, 6, 1, 4, 1, 61439, 1, 1, 2), Integer32()).setMaxAccess("readonly")
testDevice1PowerNumberOfComponents = MibScalar((1, 3, 6, 1, 4, 1, 61439, 1, 4, 1, 1), Integer32()).setMaxAccess("readonly")
testDevice1PowerTable = MibTable((1, 3, 6, 1, 4, 1, 61439, 1, 4, 1, 2), )
testDevice1PowerEntry = MibTableRow((1, 3, 6, 1, 4, 1, 61439, 1, 4, 1, 2, 1), ).setIndexNames((0, "TEST-MIB1", "powerIndex"))
powerIndex = MibTableColumn((1, 3, 6, 1, 4, 1, 61439, 1, 4, 1, 2, 1, 1), Integer32().subtype(subtypeSpec=ValueRangeConstraint(1,2147483647))).setMaxAccess("readonly")
powerId = MibTableColumn((1, 3, 6, 1, 4, 1, 61439, 1, 4, 1, 2, 1, 2), Integer32()).setMaxAccess("readonly")
powerName = MibTableColumn((1, 3, 6, 1, 4, 1, 61439, 1, 4, 1, 2, 1, 3), DisplayString().subtype(subtypeSpec=ValueSizeConstraint(0,30))).setMaxAccess("readonly")
powerState = MibTableColumn((1, 3, 6, 1, 4, 1, 61439, 1, 4, 1, 2, 1, 4), Integer32().subtype(subtypeSpec=SingleValueConstraint(1, 2,)).clone(namedValues=NamedValues(("off", 1), ("on", 2),))).setMaxAccess("readwrite")
powerVoltage = MibTableColumn((1, 3, 6, 1, 4, 1, 61439, 1, 4, 1, 2, 1, 5), Integer32().subtype(subtypeSpec=ValueRangeConstraint(1,999))).setMaxAccess("readwrite")
testDevice1FanNumberOfComponents = MibScalar((1, 3, 6, 1, 4, 1, 61439, 1, 4, 2, 1), Integer32()).setMaxAccess("readonly")
testDevice1FanTable = MibTable((1, 3, 6, 1, 4, 1, 61439, 1, 4, 2, 2), )
testDevice1FanEntry = MibTableRow((1, 3, 6, 1, 4, 1, 61439, 1, 4, 2, 2, 1), ).setIndexNames((0, "TEST-MIB1", "fanIndex"))
fanIndex = MibTableColumn((1, 3, 6, 1, 4, 1, 61439, 1, 4, 2, 2, 1, 1), Integer32().subtype(subtypeSpec=ValueRangeConstraint(1,2147483647))).setMaxAccess("readonly")
fanId = MibTableColumn((1, 3, 6, 1, 4, 1, 61439, 1, 4, 2, 2, 1, 2), Integer32()).setMaxAccess("readonly")
fanName = MibTableColumn((1, 3, 6, 1, 4, 1, 61439, 1, 4, 2, 2, 1, 3), DisplayString().subtype(subtypeSpec=ValueSizeConstraint(0,30))).setMaxAccess("readonly")
fanRpm = MibTableColumn((1, 3, 6, 1, 4, 1, 61439, 1, 4, 2, 2, 1, 4), Integer32()).setMaxAccess("readwrite")
testDevice1LedNumberOfComponents = MibScalar((1, 3, 6, 1, 4, 1, 61439, 1, 4, 3, 1), Integer32()).setMaxAccess("readonly")
testDevice1LedTable = MibTable((1, 3, 6, 1, 4, 1, 61439, 1, 4, 3, 2), )
testDevice1LedEntry = MibTableRow((1, 3, 6, 1, 4, 1, 61439, 1, 4, 3, 2, 1), ).setIndexNames((0, "TEST-MIB1", "ledIndex"))
ledIndex = MibTableColumn((1, 3, 6, 1, 4, 1, 61439, 1, 4, 3, 2, 1, 1), Integer32().subtype(subtypeSpec=ValueRangeConstraint(1,2147483647))).setMaxAccess("readonly")
ledId = MibTableColumn((1, 3, 6, 1, 4, 1, 61439, 1, 4, 3, 2, 1, 2), Integer32()).setMaxAccess("readonly")
ledName = MibTableColumn((1, 3, 6, 1, 4, 1, 61439, 1, 4, 3, 2, 1, 3), DisplayString().subtype(subtypeSpec=ValueSizeConstraint(0,30))).setMaxAccess("readonly")
ledState = MibTableColumn((1, 3, 6, 1, 4, 1, 61439, 1, 4, 3, 2, 1, 4), Integer32().subtype(subtypeSpec=SingleValueConstraint(1, 2,)).clone(namedValues=NamedValues(("off", 1), ("on", 2),))).setMaxAccess("readwrite")
ledBlinkState = MibTableColumn((1, 3, 6, 1, 4, 1, 61439, 1, 4, 3, 2, 1, 5), Integer32().subtype(subtypeSpec=SingleValueConstraint(1, 2,)).clone(namedValues=NamedValues(("off", 1), ("on", 2),))).setMaxAccess("readwrite")
ledColor = MibTableColumn((1, 3, 6, 1, 4, 1, 61439, 1, 4, 3, 2, 1, 6), Integer32()).setMaxAccess("readwrite")
mibBuilder.exportSymbols("TEST-MIB1", testDevice1FanEntry=testDevice1FanEntry, powerVoltage=powerVoltage, testDevice1Power=testDevice1Power, powerId=powerId, powerName=powerName, ledName=ledName, testDevice1LedNumberOfComponents=testDevice1LedNumberOfComponents, testDevice1RevMinor=testDevice1RevMinor, ledId=ledId, testDevice1FanTable=testDevice1FanTable, testDevice1LedTable=testDevice1LedTable, fanId=fanId, testDevice1PowerTable=testDevice1PowerTable, fanRpm=fanRpm, ledIndex=ledIndex, testDevice1Fan=testDevice1Fan, testDevice1PowerEntry=testDevice1PowerEntry, powerState=powerState, ledColor=ledColor, testEnterprise=testEnterprise, testDevice1LedEntry=testDevice1LedEntry, fanName=fanName, testDevice1PowerNumberOfComponents=testDevice1PowerNumberOfComponents, testDevice1Status=testDevice1Status, testDevice1Rev=testDevice1Rev, testDevice1RevMajor=testDevice1RevMajor, testDevice1=testDevice1, fanIndex=fanIndex, testDevice1FanNumberOfComponents=testDevice1FanNumberOfComponents, testDevice1Led=testDevice1Led, ledState=ledState, ledBlinkState=ledBlinkState, powerIndex=powerIndex)
