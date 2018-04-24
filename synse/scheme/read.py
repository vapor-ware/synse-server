"""Response scheme for the `read` endpoint."""

from synse import utils
from synse.i18n import _
from synse.log import logger
from synse.scheme.base_response import SynseResponse


class ReadResponse(SynseResponse):
    """A ReadResponse is the response data for a Synse 'read' command.

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

    Args:
        device (MetainfoResponse): The device that is being read.
        readings (list[ReadResponse]): A list of reading values returned
            from the plugin.
    """

    _data_types = {
        'string': str,
        'float': float,
        'int': utils.s_to_int,
        'bool': utils.s_to_bool,
    }

    def __init__(self, device, readings):
        self.device = device
        self.readings = readings

        self.data = {
            'type': device.type,
            'data': self.format_readings()
        }

    def format_readings(self):
        """Format the instance's readings to the read response scheme.

        Returns:
            dict: A properly formatted Read response.
        """
        logger.debug(_('Formatting read response'))
        formatted = {}

        dev_output = self.device.output
        for reading in self.readings:
            rt = reading.type

            # These fields may not be specified, e.g. in cases where it wouldn't
            # make sense for a reading unit, e.g. LED state (on/off)
            unit = None
            precision = None
            data_type = None

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

            # If the reading type does not match the supported types, we will not
            # return it, and instead will just just skip over it.
            if not found:
                logger.warning(
                    _('Found unexpected reading type "{}" for device {}')
                    .format(rt, self.device)
                )
                continue

            value = reading.value

            # Handle cases where no data was read. Currently, we consider the reading
            # to have no data if:
            #   - the ReadResponse value comes back as an empty string (e.g. "")
            #   - the ReadResponse value comes back as the string "null".
            if value == '' or value == 'null':
                logger.info(_('Reading value for {} came back as empty/null').format(rt))
                value = None

            else:
                # Set the specified precision
                if precision:
                    try:
                        value = str(round(float(value), precision))
                    except ValueError:
                        logger.warning(
                            _('Invalid value for {}: "{}"').format(data_type, value)
                        )

                # Cast to the specified type
                try:
                    value = self._data_types.get(data_type, str)(value)
                except ValueError:
                    logger.warning(_('Failed to cast "{}" to {}').format(value, data_type))

            formatted[rt] = {
                'value': value,
                'timestamp': reading.timestamp,
                'unit': unit
            }

        return formatted
