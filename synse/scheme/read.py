"""Response scheme for the `read` endpoint.
"""

from synse import utils
from synse.i18n import gettext
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

    _data_types = {
        'string': str,
        'float': float,
        'int': utils.s_to_int,
        'bool': utils.s_to_bool,
    }

    def __init__(self, device, readings):
        """Constructor for the ReadResponse class.

        Args:
            device (MetainfoResponse): The device that is being read.
            readings (list[ReadResponse]): A list of reading values returned
                from the plugin.
        """
        self.device = device
        self.readings = readings

        self.data = {
            'type': device.type,
            'data': self.format_readings()
        }

    def format_readings(self):
        """Format the instance's readings to the Read response scheme.

        Returns:
            dict: A properly formatted Read response.
        """
        logger.debug(gettext('Making read response'))
        formatted = {}

        dev_output = self.device.output
        for reading in self.readings:
            rt = reading.type

            # these fields may not be specified, e.g. in cases where it wouldn't
            # make sense for a reading unit, e.g. LED state (on/off)
            unit = None
            precision = None
            data_type = None

            logger.debug(gettext('device output: {}').format(dev_output))
            found = False
            for out in dev_output:
                if out.type == rt:
                    symbol = out.unit.symbol
                    name = out.unit.name
                    precision = out.precision
                    data_type = out.data_type

                    if symbol or name:
                        unit = {
                            'symbol': symbol,
                            'name': name
                        }

                    found = True
                    break

            # if the reading type does not match the supported types, we will not
            # return it, and instead will just just skip over it.
            if not found:
                logger.warning(
                    gettext('Found unexpected reading type "{}" for device {}')
                    .format(rt, self.device)
                )
                continue

            logger.debug(gettext('  Precision: {}').format(precision))
            value = reading.value

            # Handle empty string.
            if value == '':
                value = None

            else:
                # set the specified precision
                if precision:
                    value = str(round(float(value), precision))

                # cast to the specified type
                try:
                    value = self._data_types.get(data_type, str)(value)
                except ValueError:
                    logger.warning(gettext('Failed to convert "{}" to {}').format(value, data_type))

            formatted[rt] = {
                'value': value,
                'timestamp': reading.timestamp,
                'unit': unit
            }

        return formatted
