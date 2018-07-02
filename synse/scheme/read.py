"""Response scheme for the `read` endpoint."""

from synse.i18n import _
from synse.log import logger
from synse.scheme.base_response import SynseResponse


class ReadResponse(SynseResponse):
    """A ReadResponse is the response data for a Synse 'read' command.

    Response Example:
        {
          "type": "humidity",
          "data": [
            {
              "info": "",
              "type": "temperature",
              "value": 123,
              "unit": {
                "symbol": "C",
                "name": "degrees celsius"
              },
              "timestamp": "2017-11-10 09:08:07"
            },
            {
              "info": "",
              "type": "humidity",
              "value": 123,
              "unit": {
                "symbol": "%",
                "name": "percent"
              },
              "timestamp": "2017-11-10 09:08:07"
            }
          ]
        }

    Args:
        device (Device): The device that is being read.
        readings (list[Reading]): A list of reading values returned
            from the plugin.
    """

    def __init__(self, device, readings):
        self.device = device
        self.readings = readings

        self.data = {
            'kind': device.kind,
            'data': self.format_readings()
        }

    def format_readings(self):
        """Format the instance's readings to the read response scheme.

        Returns:
            dict: A properly formatted Read response.
        """
        logger.debug(_('Formatting read response'))
        formatted = []

        dev_output = self.device.output
        for reading in self.readings:
            rt = reading.type

            # These fields may not be specified, e.g. in cases where it wouldn't
            # make sense for a reading unit, e.g. LED state (on/off)
            unit = None
            precision = None

            found = False
            for out in dev_output:
                if out.type == rt:
                    symbol = out.unit.symbol
                    name = out.unit.name
                    precision = out.precision

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

            # The value is stored in a protobuf oneof block, so we need to figure out
            # which field it is in, and extract it. If no field is set, take the reading
            # value to be None.
            value = None

            field = reading.WhichOneof('value')
            if field is not None:
                value = getattr(reading, field)

            # FIXME (etd) is this block still relevent with the grpc changes? I don't think it is.
            # Handle cases where no data was read. Currently, we consider the reading
            # to have no data if:
            #   - the ReadResponse value comes back as an empty string (e.g. "")
            #   - the ReadResponse value comes back as the string "null".
            if value == '' or value == 'null':
                logger.info(_('Reading value for {} came back as empty/null').format(rt))
                value = None

            else:
                # Set the specified precision
                if precision and isinstance(value, float):
                    value = round(value, precision)

            formatted.append({
                'value': value,
                'timestamp': reading.timestamp,
                'unit': unit,
                'type': rt,
                'info': reading.info,
            })

        return formatted
