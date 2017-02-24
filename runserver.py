#!/usr/bin/env python
""" OpenDCRE Server Runner - Used to launch OpenDCRE from package
via flask/nginx

    Author:  andrew
    Date:    7/28/2015

    \\//
     \/apor IO

-------------------------------
Copyright (C) 2015-17  Vapor IO

This file is part of OpenDCRE.

OpenDCRE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

OpenDCRE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenDCRE.  If not, see <http://www.gnu.org/licenses/>.
"""
from opendcre_southbound import main
import sys

# leave this import, it is used by uwsgi
from opendcre_southbound import app

if len(sys.argv) == 3:
    main(serial_port=sys.argv[1], hardware=sys.argv[2])
elif len(sys.argv) == 2:
    main(serial_port=sys.argv[1])
else:
    main()
