#!/usr/bin/python
'''
   Virtual BMC for testing of IPMI bridge from OpenDCRE->IPMI.

   Author:  andrew
   Date:    10/20/2015

        \\//
         \/apor IO
'''
import socket
import json
import sys

UDP_IP = '0.0.0.0'
UDP_PORT = 623
TERMINATE = False

file = open(sys.argv[1], 'r')
data = file.read()
configuration = json.loads(data)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

response_index = 0

while not TERMINATE:
    data, addr = sock.recvfrom(512)
    '''print addr,
    for x in data:
        print hex(ord(x)) ,
    print ''
    print '>> ',
    for x in configuration['responses'][response_index]:
        print hex(x),'''
    sock.sendto(bytearray(configuration['responses'][response_index]), addr)
    response_index += 1
    if configuration['repeat']:
        response_index %= len(configuration['responses'])
    else:
        if response_index >= len(configuration['responses']):
            TERMINATE = True
