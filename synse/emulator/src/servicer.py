"""
"""

import datetime
import random
from uuid import uuid4 as uuid

import grpc

from synse.emulator.src import devices
from synse.proto import api_pb2, api_pb2_grpc

STATUS_UNKNOWN = 0
STATUS_PENDING = 1
STATUS_WRITING = 2
STATUS_DONE = 3

STATE_OK = 0
STATE_ERR = 1

transactions = {}


reading_type_lookup = {
    'unknown': api_pb2.UNKNOWN,
    'temperature': api_pb2.TEMPERATURE,
    'differential_pressure': api_pb2.DIFFERENTIAL_PRESSURE,
    'airflow': api_pb2.AIRFLOW,
    'humidity': api_pb2.HUMIDITY,
    'led_state': api_pb2.LED_STATE,
    'led_blink': api_pb2.LED_BLINK
}


class InternalApiServicer(api_pb2_grpc.InternalApiServicer):
    """
    """

    def Read(self, request, context):
        """

        Args:
            request ():
            context ():
        """
        uid = request.uid

        dev = devices.find_device(uid)
        if dev is None:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('Could not find device with id {}'.format(uid))
            return api_pb2.ReadResponse()

        # FIXME -- for now, we'll only get the first thing in the data list
        #       this needs to be improved because in cases where there are multiple
        #       readings (like LED, humidity, ...) this would set the same value
        #       to both which is not what we want.
        for output in dev.output:

            if dev.data:
                val = dev.data[0]
            else:
                _min = output.range.min
                _max = output.range.max

                if _min is not None and _max is not None:
                    val = random.randint(_min, _max)
                else:
                    val = 'unknown'

            yield api_pb2.ReadResponse(
                timestamp=str(datetime.datetime.utcnow()),
                type=reading_type_lookup.get(output.type),
                value=str(val)
            )

    def Write(self, request, context):
        """

        Args:
            request ():
            context ():
        """
        uid = request.uid
        data = request.data

        dev = devices.find_device(uid)
        if not dev.is_writable:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details('The device "{}" is not writable.'.format(dev.type))
            return api_pb2.TransactionId()

        dev.data = data

        _id = str(uuid())
        resp = api_pb2.TransactionId(id=_id)

        transactions[_id] = STATUS_PENDING
        return resp

    def Metainfo(self, request, context):
        """

        Args:
            request ():
            context ():
        """
        for device in devices.cache:
            yield device.to_metaresponse()

    def TransactionCheck(self, request, context):
        """

        Args:
            request ():
            context ():
        """
        _id = request.id

        if _id not in transactions:
            status = STATUS_UNKNOWN
            state = STATE_ERR

        else:
            state = STATE_OK
            status = transactions[_id]

            # move the state along to the next state level.
            if status == STATUS_PENDING:
                transactions[_id] = STATUS_WRITING
            elif status == STATUS_WRITING:
                transactions[_id] = STATUS_DONE

        return api_pb2.WriteResponse(
            timestamp=str(datetime.datetime.now()),
            status=status,
            state=state
        )
