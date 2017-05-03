#!/usr/bin/env python
""" A definition of all auth type codes for the IPMI protocol.

    Author: Erick Daniszewski
    Date:   09/02/2016
    
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
