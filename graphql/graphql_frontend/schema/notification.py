""" Notification Schema

    Author: Thomas Rampelberg
    Date:   2/27/2017

    \\//
     \/apor IO
"""

import graphene


class NotificationSource(graphene.ObjectType):
    BoardID = graphene.String()
    DeviceID = graphene.String(required=True)
    DeviceType = graphene.String(required=True)
    Field = graphene.String(required=True)
    RackID = graphene.String()
    Reading = graphene.String(required=True)
    ZoneID = graphene.String(required=True)


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
