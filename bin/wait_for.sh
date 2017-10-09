#!/bin/bash
# wait_for.sh
#
# this waits for the version endpoint of synse server running on the
# specified host and port to be reachable. when the endpoint becomes
# reachable, this indicates that the Flask application has completed
# registration and is now serving the endpoints.
#
# ---------------------------------------------------------------------
# Copyright (C) 2015-17  Vapor IO
#
# This file is part of Synse.
#
# Synse is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Synse is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Synse.  If not, see <http://www.gnu.org/licenses/>.
# ---------------------------------------------------------------------

host=$1
port=$2

echo "waiting for $host:$port"
until $(curl --output /dev/null --silent --fail http://${host}:${port}/synse/version); do
    printf "."
    sleep 1
done

printf "\n$host:$port ready.\n"