#!/usr/bin/env python
""" A definition of all auth type codes for the IPMI protocol.

    Author: Erick Daniszewski
    Date:   09/02/2016
    
    \\//
     \/apor IO
"""

# AUTHENTICATION TYPES
# ---------------------------
# 0h = none
# 1h = MD2
# 2h = MD5
# 3h = reserved
# 4h = straight password/key
# 5h = OEM proprietary
# 6h = RMCP+
# ---------------------------
NONE = 0x00
MD2  = 0x01
MD5  = 0x02
PWD  = 0x04
OEM  = 0x05
RMCP = 0x06
