"""Response scheme for the /read endpoint.
"""

from synse.log import logger
from synse.scheme.base_response import SynseResponse


class ReadResponse(SynseResponse):
    """A ReadResponse is the response data for a Synse 'read' command.

    The JSON response returned by the Synse endpoint, constructed from
    the data here, should follow the scheme:

    Response Scheme:
        <TODO - WRITE SCHEME FOR RESPONSE>

    Response Example:
        {
          "type": "humidity",
          "data": {
            "temperature": {
              "value": 123,
              "unit": {
                "symbol": "C",
                "name": "degrees celsius"
              },
              "timestamp": "2017-11-10 09:08:07"
            },
            "humidity": {
              "value": 123,
              "unit": {
                "symbol": "%",
                "name": "percent"
              },
              "timestamp": "2017-11-10 09:08:07"
            }
          }
        }

    """

    def __init__(self, device, readings):
        """Constructor for the ReadResponse class.

        Args:
            device (): the device that is being read.
            readings (list[]): a list of reading values returned from the
                background process.
        """
        self.device = device
        self.readings = readings

        self.data = {
            'type': device.type,
            'data': self.format_readings()
        }

    def format_readings(self):
        """
        """
        logger.debug('Making read response')
        formatted = {}

        dev_output = self.device.output
        for reading in self.readings:
            rt = reading.type

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
