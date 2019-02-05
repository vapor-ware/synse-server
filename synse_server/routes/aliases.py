"""The aliased routes that make up the Synse Server HTTP API."""

from sanic import Blueprint

from synse_server import commands, const, errors, validate
from synse_server.i18n import _
from synse_server.log import logger
from synse_server.version import __api_version__

bp = Blueprint(__name__, url_prefix='/synse/' + __api_version__)


@bp.route('/led/<rack>/<board>/<device>')
async def led_route(request, rack, board, device):
    """Endpoint to read/write LED device data.

    This route is an alias for the core `read` functionality when there
    are no valid query parameters specified. It is an alias for the core
    `write` functionality when there are valid query parameters specified.

    Supported Query Parameters:
        state: The LED state to set (on|off|blink)
        color: The LED color to set. This must be a hexadecimal string
            between 000000 and ffffff.

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The rack which the led device resides on.
        board (str): The board which the led device resides on.
        device (str): The LED device.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    await validate.validate_device_type(const.LED_TYPES, rack, board, device)

    # Get the valid query parameters. If unsupported query parameters
    # are specified, this will raise an error.
    qparams = validate.validate_query_params(
        request.raw_args,
        'state', 'color'
    )
    param_state = qparams.get('state')
    param_color = qparams.get('color')

    # If any of the parameters are specified, this will be a write request
    # using those parameters.
    if any((param_state, param_color)):
        logger.debug(_('LED alias route: writing (query parameters: {})').format(qparams))
        data = []

        if param_state:
            if param_state not in const.led_states:
                raise errors.InvalidUsage(
                    _('Invalid LED state "{}". Must be one of: {}').format(
                        param_state, const.led_states)
                )

            data.append({
                'action': 'state',
                'raw': param_state
            })

        if param_color:
            try:
                assert 0x000000 <= int(param_color, 16) <= 0xFFFFFF
            except Exception as e:
                raise errors.InvalidUsage(
                    _('Invalid color value ({}). Must be a hexadecimal '
                      'string between 000000 and FFFFFF').format(param_color)
                ) from e

            data.append({
                'action': 'color',
                'raw': param_color
            })

        logger.debug(_('LED data to write: {}').format(data))
        transactions = None
        for d in data:
            t = await commands.write(rack, board, device, d)
            if not transactions:
                transactions = t
            else:
                transactions.data.extend(t.data)

        return transactions.to_json()

    # Otherwise, we just read from the device.
    else:
        logger.debug(_('LED alias route: reading'))
        reading = await commands.read(rack, board, device)
        return reading.to_json()


@bp.route('/fan/<rack>/<board>/<device>')
async def fan_route(request, rack, board, device):
    """Endpoint to read/write fan device data.

    This route is an alias for the core `read` functionality when there
    are no valid query parameters specified. It is an alias for the core
    `write` functionality when there are valid query parameters specified.

    Supported Query Parameters:
        speed: The fan speed to set, in RPM.
        speed_percent: The fan speed to set, in percent.

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The rack which the fan device resides on.
        board (str): The board which the fan device resides on.
        device (str): The fan device.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    await validate.validate_device_type(const.FAN_TYPES, rack, board, device)

    # Get the valid query parameters. If unsupported query parameters
    # are specified, this will raise an error.
    qparams = validate.validate_query_params(
        request.raw_args,
        'speed',  # speed in rpm
        'speed_percent'  # speed of 0 (off) or 10% to 100%
    )

    param_speed_rpm = qparams.get('speed')
    param_speed_percent = qparams.get('speed_percent')

    # Only one of 'speed' and 'speed_percent' can be specified at a time.
    # TODO (etd): this could be generalized and incorporated into the validation
    #   done above, e.g. validate_query_params(request.raw_args, OneOf(['speed', 'speed_percent']))
    if all((param_speed_rpm, param_speed_percent)):
        raise errors.InvalidUsage(
            _('Invalid query params: Can only specify one of "speed" and '
              '"speed_percent", but both were given')
        )

    # If either of the parameters are specified, this will be a write request
    # using those parameters.
    if any((param_speed_rpm, param_speed_percent)):
        logger.debug(_('Fan alias route: writing (query parameters: {})').format(qparams))

        # Set the fan speed by RPM. No validation on the fan speed is done here,
        # as it is up to the underlying implementation to validate and fail as
        # needed. The max and min allowable speeds vary by fan motor.
        if param_speed_rpm:
            logger.debug(_('Setting fan speed by RPM'))
            data = {
                'action': 'speed',
                'raw': param_speed_rpm,
            }
            transaction = await commands.write(rack, board, device, data)
            return transaction.to_json()

        # Set the fan speed by percent (duty cycle). No validation on the fan
        # speed is done here, as it is up to the underlying implementation to
        # validate and fail as needed. The max and min allowable speeds vary
        # by fan motor.
        if param_speed_percent:
            logger.debug(_('Setting fan speed by percent'))
            data = {
                'action': 'speed_percent',
                'raw': param_speed_percent,
            }
            transaction = await commands.write(rack, board, device, data)
            return transaction.to_json()

    # Otherwise, we just read from the device.
    else:
        logger.debug(_('Fan alias route: reading'))
        reading = await commands.read(rack, board, device)
        return reading.to_json()


@bp.route('/power/<rack>/<board>/<device>')
async def power_route(request, rack, board, device):
    """Endpoint to read/write power device data.

    This route is an alias for the core `read` functionality when there
    are no valid query parameters specified. It is an alias for the core
    `write` functionality when there are valid query parameters specified.

    Supported Query Parameters:
        state: The power state to set (on|off|cycle)

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The rack which the power device resides on.
        board (str): The board which the power device resides on.
        device (str): The power device.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    await validate.validate_device_type(const.POWER_TYPES, rack, board, device)

    # Get the valid query parameters. If unsupported query parameters
    # are specified, this will raise an error.
    qparams = validate.validate_query_params(
        request.raw_args,
        'state'
    )
    param_state = qparams.get('state')

    # If any of the parameters are specified, this will be a write request
    # using those parameters.
    if param_state is not None:
        logger.debug(_('Power alias route: writing (query parameters: {})').format(qparams))

        if param_state not in const.power_actions:
            raise errors.InvalidUsage(
                _('Invalid power state "{}". Must be one of: {}').format(
                    param_state, const.power_actions)
            )

        data = {
            'action': 'state',
            'raw': param_state
        }
        transaction = await commands.write(rack, board, device, data)
        return transaction.to_json()

    # Otherwise, we just read from the device.
    else:
        logger.debug(_('Power alias route: reading'))
        reading = await commands.read(rack, board, device)
        return reading.to_json()


@bp.route('/boot_target/<rack>/<board>/<device>')
async def boot_target_route(request, rack, board, device):
    """Endpoint to read/write boot target device data.

    This route is an alias for the core `read` functionality when there
    are no valid query parameters specified. It is an alias for the core
    `write` functionality when there are valid query parameters specified.

    Supported Query Parameters:
        target: The boot target to set (hdd|pxe)

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The rack which the system resides on.
        board (str): The board which the system resides on.
        device (str): The system device.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    await validate.validate_device_type(const.BOOT_TARGET_TYPES, rack, board, device)

    # Get the valid query parameters. If unsupported query parameters
    # are specified, this will raise an error.
    qparams = validate.validate_query_params(
        request.raw_args,
        'target'
    )
    param_target = qparams.get('target')

    # If any of the parameters are specified, this will be a write request
    # using those parameters.
    if param_target is not None:
        logger.debug(_('Boot target alias route: writing (query parameters: {})').format(qparams))

        if param_target not in const.boot_targets:
            raise errors.InvalidUsage(
                _('Invalid boot target "{}". Must be one of: {}').format(
                    param_target, const.boot_targets)
            )

        data = {
            'action': 'target',
            'raw': param_target
        }
        transaction = await commands.write(rack, board, device, data)
        return transaction.to_json()

    # Otherwise, we just read from the device.
    else:
        logger.debug(_('Boot target alias route: reading'))
        reading = await commands.read(rack, board, device)
        return reading.to_json()


@bp.route('/lock/<rack>/<board>/<device>')
async def lock_route(request, rack, board, device):
    """Endpoint to read/write lock device data.

    This route is an alias for the core `read` functionality when there
    are no valid query parameters specified. It is an alias for the core
    `write` functionality when there are valid query parameters specified.

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The rack which the lock resides on.
        board (str): The board which the lock resides on.
        device (str): The lock device.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    await validate.validate_device_type(const.LOCK_TYPES, rack, board, device)

    # Get the valid query parameters. If unsupported query parameters
    # are specified, this will raise an error.
    qparams = validate.validate_query_params(
        request.raw_args,
        'action'
    )
    param_action = qparams.get('action')

    # If any of the parameters are specified, this will be a write request
    # using those parameters.
    if param_action is not None:
        logger.debug(_('Lock alias route: writing (query parameters: {})').format(qparams))

        if param_action not in const.lock_actions:
            raise errors.InvalidUsage(
                _('Invalid boot target "{}". Must be one of: {}').format(
                    param_action, const.lock_actions)
            )

        data = {
            'action': param_action,
        }
        transaction = await commands.write(rack, board, device, data)
        return transaction.to_json()

    # Otherwise, we just read from the device.
    else:
        logger.debug(_('Lock alias route: reading'))
        reading = await commands.read(rack, board, device)
        return reading.to_json()
