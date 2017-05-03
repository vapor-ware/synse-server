""" Notification Schema

    Author: Thomas Rampelberg
    Date:   2/27/2017

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

import graphene


class NotificationSource(graphene.ObjectType):
    BoardID = graphene.String()
    DeviceID = graphene.String()
    DeviceType = graphene.String()
    Field = graphene.String()
    RackID = graphene.String()
    Reading = graphene.String()
    ZoneID = graphene.String()


class Notification(graphene.ObjectType):
    _id = graphene.String(required=True)
    code = graphene.Int(required=True)
    resolved_on = graphene.String()
    severity = graphene.String(required=True)
    source = graphene.Field(NotificationSource, required=True)
    status = graphene.String(required=True)
    text = graphene.String(required=True)
    timestamp = graphene.String(required=True)

    @staticmethod
    def build(body):
        return Notification(
            source=NotificationSource(**body.pop("source")), **body)
