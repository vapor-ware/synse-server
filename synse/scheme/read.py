"""

"""

from synse.log import logger
from synse.proto import util as putil
from synse.scheme.base_response import SynseResponse


class ReadResponse(SynseResponse):
    """ A ReadResponse is the response data for a Synse 'read' command.

    The JSON response returned by the Synse endpoint, constructed from
    the data here, should follow the scheme:

    <TODO - WRITE SCHEME FOR RESPONSE>

    Example:

        {
          "meta": {
            "board": "00000001",
            "device": "0001",
            "rack": "rack_1",
            "device_type": "humidity"
          },
          "sensors": [
            "temperature",
            "humidity"
          ],
          "data": {
            "temperature": {
              "value": 123,
              "unit": {
                "symbol": "C",
                "name": "degrees celsius"
              },
              "timestamp": "123123123"
            },
            "humidity": {
              "value": 123,
              "unit": {
                "symbol": "%",
                "name": "percent"
              },
              "timestamp": "12312415"
            }
          }
        }
    """

    def __init__(self, device, readings):
        """

        Args:
            device (): the device that is being read.
            readings (list[]): a list of reading values returned from the
                background process.
        """
        self.device = device
        self.readings = readings

        self.data = {
            'meta': {
                'rack': device.location.rack,
                'board': device.location.board,
                'device': device.location.device,
                'device_type': device.type
            },
            'sensors': [putil.reading_type_name(r.type) for r in readings],
            'data': self.format_readings()
        }

    def format_readings(self):
        """
        """
        logger.debug('Making read response')
        formatted = {}

        dev_output = self.device.output
        for reading in self.readings:
            rt = putil.reading_type_name(reading.type)

            # these fields may not be specified, e.g. in cases where it wouldn't
            # make sense for a reading kind, e.g. LED state (on/off)
            symbol = ''
            name = ''
            precision = None

            logger.debug('device output: {}'.format(dev_output))
            for out in dev_output:
                logger.debug('output: {}, reading: {}'.format(out.type, rt))
                if out.type == rt:
                    symbol = out.unit.symbol
                    name = out.unit.name
                    precision = out.precision
                    break

            logger.debug('  Precision: {}'.format(precision))
            value = reading.value
            if precision:
                value = round(float(value), precision)

            formatted[rt] = {
                'value': value,
                'timestamp': reading.timestamp,
                'unit': {
                    'symbol': symbol,
                    'name': name
                }
            }

        return formatted
