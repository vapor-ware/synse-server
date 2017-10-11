""" Manage the configuration for the emulated devices.
"""

import datetime
import logging
import os

import yaml

from synse.proto import api_pb2

logger = logging.getLogger(__name__)

_pwd = os.path.dirname(__file__)
_cfg_dir = os.path.normpath(os.path.join(_pwd, '../config'))


cache = []


def _load(path):
    """ Load in the configuration(s) at the given path.
    """
    data = []

    for _file in os.listdir(path):
        filepath = os.path.join(path, _file)
        if os.path.isfile(filepath) and os.path.splitext(filepath)[1] in ['.yml', '.yaml']:
            with open(filepath, 'r') as f:
                data.append(yaml.load(f))

    return data


def load_proto_cfg():
    """ Load in the prototype configuration(s) for the emulator.
    """
    return _load(os.path.join(_cfg_dir, 'proto'))


def load_sensor_cfg():
    """ Load in the sensor configuration(s) for the emulator.
    """
    return _load(os.path.join(_cfg_dir, 'sensor'))


def make_devices():
    """ Create Device objects for all of the configured devices.
    """
    proto_cfg = load_proto_cfg()
    sensor_cfg = load_sensor_cfg()

    # iterate through all of the configured sensors. if there are no
    # configured sensors, then we will have no devices.
    for sensor in sensor_cfg:

        # we use the sensor type and model to match it up with the
        # corresponding prototype configuration.
        t = sensor['type']
        m = sensor['model']

        proto = None
        for p in proto_cfg:
            if p['type'] == t and p['model'] == m:
                proto = p
                break

        # if we didn't find a matching protocol, log a message and
        # move on to the next sensor.
        if proto is None:
            logger.warning('Did not find prototype for sensor: {}'.format(sensor))
            continue

        # we now have the prototype config and the sensor config so
        # we can create the unified device. we do this for every configured
        # sensor device
        for device in sensor['devices']:
            device['location'] = sensor['locations'][device['location']]
            cache.append(Device(proto, device))
    print('made devices: {}'.format(cache))


def find_device(uid):
    """

    Args:
        uid (str):
    """
    for d in cache:
        if d.uid == uid:
            return d
    return None


class Device(object):
    """ Object which holds the information related to a single device.
    """

    _writable_devices = ['emulated-fan', 'emulated-led']

    def __init__(self, proto, sensor):
        self._proto_cfg = proto
        self._sensor_cfg = sensor

        self.type = proto['type']
        self.model = proto['model']
        self.manufacturer = proto['manufacturer']
        self.protocol = proto['protocol']
        self.output = [Output(o) for o in proto['output']]

        self.comment = sensor['comment']
        self.info = sensor['info']
        self.location = Location(
            rack=sensor['location']['rack'],
            board=sensor['location']['board'],
            device=sensor['id']
        )

        self.uid = str(self.location.string() + self.type)

        # for the emulator, we defined which devices are writable and
        # which are not. this way, we can simulate failing to write to
        # a device which can't be written to.
        self.is_writable = self.type in self._writable_devices
        self.data = []

    def to_metaresponse(self):
        """
        """
        return api_pb2.MetainfoResponse(
            timestamp=str(datetime.datetime.utcnow()),
            uid=self.uid,
            type=self.type,
            model=self.model,
            manufacturer=self.manufacturer,
            protocol=self.protocol,
            info=self.info,
            comment=self.comment,
            location=self.location.to_metalocation(),
            output=[o.to_metaoutput() for o in self.output]
        )


class Output(object):
    """
    """

    def __init__(self, output_cfg):
        self._output_cfg = output_cfg

        self.type = output_cfg['type']

        # the below are optional.
        self.unit = Unit(output_cfg.get('unit', {}))
        self.precision = output_cfg.get('precision')
        self.range = Range(output_cfg.get('range', {}))

    def to_metaoutput(self):
        """
        """
        return api_pb2.MetaOutput(
            type=self.type,
            unit=self.unit.to_metaunit(),
            precision=self.precision,
            range=self.range.to_metarange()
        )


class Unit(object):
    """
    """

    def __init__(self, unit_cfg):
        self._unit_cfg = unit_cfg

        self.name = unit_cfg.get('name')
        self.symbol = unit_cfg.get('symbol')

    def to_metaunit(self):
        return api_pb2.MetaOutputUnit(
            name=self.name,
            symbol=self.symbol
        )


class Range(object):
    """
    """

    def __init__(self, range_cfg):
        self._range_cfg = range_cfg

        self.min = range_cfg.get('min')
        self.max = range_cfg.get('max')

    def to_metarange(self):
        return api_pb2.MetaOutputRange(
            min=self.min,
            max=self.max
        )


class Location(object):
    """
    """

    def __init__(self, rack, board, device):
        self.rack = str(rack)
        self.board = str(board)
        self.device = str(device)

    def string(self):
        return self.rack + self.board + self.device

    def to_metalocation(self):
        return api_pb2.MetaLocation(
            rack=self.rack,
            board=self.board,
            device=self.device
        )
