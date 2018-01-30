"""The aliased routes that make up the Synse Server JSON API.
"""
# pylint: disable=no-else-return

from sanic import Blueprint

from synse import commands, const, errors, validate
from synse.version import __api_version__

bp = Blueprint(__name__, url_prefix='/synse/' + __api_version__)


@bp.route('/led/<rack>/<board>/<device>')
async def led_route(request, rack, board, device):
    """Endpoint to read/write LED device data.

    If no state, color, or blink is specified through request parameters,
    this will translate to a device read. Otherwise, if any valid request
    parameter is specified, this will translate to a device write.

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The rack which the led device resides on.
        board (str): The board which the led device resides on.
        device (str): The LED device.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    await validate.validate_device_type(const.TYPE_LED, rack, board, device)

    param_state = request.raw_args.get('state')
    param_blink = request.raw_args.get('blink')
    param_color = request.raw_args.get('color')

    # if any of the parameters are specified, then this will be
    # a write request for those parameters that are specified.
    if any((param_state, param_blink, param_color)):
        data = []

        if param_state:
            if param_state not in (const.LED_ON, const.LED_OFF):
                # FIXME - improve error message here. provide valid states.
                raise errors.InvalidArgumentsError(
                    gettext('Invalid state: {}').format(param_state)
                )

            data.append({
                'action': 'state',
                'raw': param_state
            })

        if param_blink:
            if param_blink not in (const.LED_BLINK, const.LED_STEADY):
                # FIXME - improve error message here. provide valid states.
                raise errors.InvalidArgumentsError(
                    gettext('Invalid blink state: {}').format(param_blink)
                )

            data.append({
                'action': 'blink',
                'raw': param_blink
            })

        if param_color:
            try:
                assert 0x000000 <= int(param_color, 16) <= 0xFFFFFF
            except Exception as e:
                raise errors.InvalidArgumentsError(
                    gettext('Invalid color value ({}). Must be a hexadecimal '
                            'string between 000000 and FFFFFF.').format(param_color)
                ) from e

            data.append({
                'action': 'color',
                'raw': param_color
            })

        transactions = None
        for d in data:
            t = await commands.write(rack, board, device, d)
            if not transactions:
                transactions = t
            else:
                transactions.data.extend(t.data)

        return transactions.to_json()

    # otherwise, we just read from the device
    else:
        reading = await commands.read(rack, board, device)
        return reading.to_json()


@bp.route('/fan/<rack>/<board>/<device>')
async def fan_route(request, rack, board, device):
    """Endpoint to read/write fan device data.

    If no fan speed is specified through request parameters, this will
    translate to a device read. Otherwise, if a valid request parameter
    is specified, this will translate to a device write.

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The rack which the fan device resides on.
        board (str): The board which the fan device resides on.
        device (str): The fan device.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    await validate.validate_device_type(const.TYPE_FAN, rack, board, device)

    param_speed = request.raw_args.get('speed')

    # if a request parameter is specified, this will translate to a
    # write request.
    if param_speed is not None:
        # FIXME - is the below true? could we check against the device prototype's
        #   "range.min" and "range.max" fields for this?
        # no validation is done on the fan speed. valid fan speeds vary based on
        # fan make/model, so it is up to the underlying implementation to do the
        # validation.
        data = {
            'action': 'speed',
            'raw': param_speed
        }
        transaction = await commands.write(rack, board, device, data)
        return transaction.to_json()

    # if no request parameter is specified, this will translate to a
    # read request.
    else:
        reading = await commands.read(rack, board, device)
        return reading.to_json()


@bp.route('/power/<rack>/<board>/<device>')
async def power_route(request, rack, board, device):
    """Endpoint to read/write power device data.

    If no state is specified through request parameters, this will
    translate to a device read. Otherwise, if a valid request parameter
    is specified, this will translate to a device write.

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The rack which the power device resides on.
        board (str): The board which the power device resides on.
        device (str): The power device.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    await validate.validate_device_type(const.TYPE_POWER, rack, board, device)

    param_state = request.raw_args.get('state')

    # if a request parameter is specified, this will translate to a
    # write request.
    if param_state is not None:
        if param_state not in (const.PWR_ON, const.PWR_OFF, const.PWR_CYCLE):
            # FIXME - improve message, add valid states
            raise errors.InvalidArgumentsError(
                gettext('Invalid power state: {}').format(param_state)
            )

        data = {
            'action': 'state',
            'raw': param_state
        }
        transaction = await commands.write(rack, board, device, data)
        return transaction.to_json()

    # if no request parameter is specified, this will translate to a
    # read request.
    else:
        reading = await commands.read(rack, board, device)
        return reading.to_json()


@bp.route('/boot_target/<rack>/<board>/<device>')
async def boot_target_route(request, rack, board, device):
    """Endpoint to read/write boot target device data.

    If no target is specified through request parameters, this will
    translate to a device read. Otherwise, if a valid request parameter
    is specified, this will translate to a device write.

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The rack which the system resides on.
        board (str): The board which the system resides on.
        device (str): The system device.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    await validate.validate_device_type(const.TYPE_SYSTEM, rack, board, device)

    param_target = request.raw_args.get('target')

    # if a request parameter is specified, this will translate to a
    # write request.
    if param_target is not None:
        if param_target not in (const.BT_PXE, const.BT_HDD):
            # FIXME - add valid targets to the error message..
            raise errors.InvalidArgumentsError(
                gettext('Invalid boot target: {}').format(param_target)
            )

        data = {
            'action': 'target',
            'raw': param_target
        }
        transaction = await commands.write(rack, board, device, data)
        return transaction.to_json()

    # if no request parameter is specified, this will translate to a
    # read request.
    else:
        reading = await commands.read(rack, board, device)
        return reading.to_json()
