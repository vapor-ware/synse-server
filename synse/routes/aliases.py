"""The aliased routes that make up the Synse Server JSON API.
"""
# pylint: disable=no-else-return

from sanic import Blueprint

from synse import commands, const, errors, validate
from synse.i18n import gettext
from synse.log import logger
from synse.version import __api_version__

bp = Blueprint(__name__, url_prefix='/synse/' + __api_version__)


@bp.route('/led/<rack>/<board>/<device>')
async def led_route(request, rack, board, device):
    """Endpoint to read/write LED device data.

    If no state or color is specified through request parameters,
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

    qparams = validate.validate_query_params(
        request.raw_args,
        'state', 'color'
    )

    param_state = qparams.get('state')
    param_color = qparams.get('color')

    # if any of the parameters are specified, then this will be
    # a write request for those parameters that are specified.
    if any((param_state, param_color)):
        data = []

        if param_state:
            if param_state not in const.led_states:
                raise errors.InvalidArgumentsError(
                    gettext('Invalid state "{}". Must be one of {}').format(
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
    logger.info('fan_route. request: {}, request.raw_args: {}'.format(request, request.raw_args))

    await validate.validate_device_type(const.TYPE_FAN, rack, board, device)

    qparams = validate.validate_query_params(
        request.raw_args,
        'speed', # speed in rpm
        'speed_percent' # speed of 0 (off) or 10% to 100%
    )

    # If there are no query parameters, this is a read request.
    if len(request.raw_args) == 0:
        logger.info('fan_route. Read request')
        reading = await commands.read(rack, board, device)
        return reading.to_json()

    # Get the first key in request.raw_args. Example: request.raw_args: {'speed': '0'}
    if len(request.raw_args) == 1:

        # Set fan speed by rpm.
        if list(request.raw_args)[0] == 'speed':
            param_speed = qparams.get('speed')
            logger.info(
                'fan_route. set speed: request {}, raw_args {}'.format(
                    request, request.raw_args))

            # if a request parameter is specified, this will translate to a
            # write request.
            if param_speed is not None:
                # Fan speed in rpm verification is done in fan controller code.
                # It varies by the motor attached to the controller, so no need
                # to try to verify here in this context.
                data = {
                    'action': 'speed',
                    'raw': param_speed,
                }
                transaction = await commands.write(rack, board, device, data)
                return transaction.to_json()

        # Set fan speed by percent (0 or 10 to 100 normally)
        elif list(request.raw_args)[0] == 'speed_percent':
            param_speed_percent = qparams.get('speed_percent')
            logger.info(
                'fan_route. set speed: request {}, raw_args {}'.format(
                    request, request.raw_args))

            # Percentage verification is done on a lower level below here, so
            # just pass the parameters on.
            data = {
                'action': 'speed_percent',
                'raw': param_speed_percent,
            }
            transaction = await commands.write(rack, board, device, data)
            return transaction.to_json()

        else:
            raise errors.InvalidArgumentsError(
                gettext('Invalid query param: {} (valid params: {})').format(
                    list(request.raw_args)[0], qparams))

    # This has to be an error.
    else:
        raise errors.InvalidArgumentsError(
            gettext('Invalid query param: {} (valid params: {})').format(
                list(request.raw_args), qparams))


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

    qparams = validate.validate_query_params(
        request.raw_args,
        'state'
    )

    param_state = qparams.get('state')

    # if a request parameter is specified, this will translate to a
    # write request.
    if param_state is not None:
        if param_state not in const.power_actions:
            raise errors.InvalidArgumentsError(
                gettext('Invalid power state "{}". Must be one of: {}').format(
                    param_state, const.power_actions)
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

    qparams = validate.validate_query_params(
        request.raw_args,
        'target'
    )

    param_target = qparams.get('target')

    # if a request parameter is specified, this will translate to a
    # write request.
    if param_target is not None:
        if param_target not in const.boot_targets:
            raise errors.InvalidArgumentsError(
                gettext('Invalid boot target "{}". Must be one of: {}').format(
                    param_target, const.boot_targets)
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


@bp.route('/lock/<rack>/<board>/<device>')
async def lock_route(request, rack, board, device): # pylint: disable=unused-argument
    """Endpoint to read/write lock device data.

    If no lock action is specified through the request parameters,
    this will translate to a device read. Otherwise, if a valid request
    parameter is specified, this will translate to a device write.

    Args:
        request (sanic.request.Request): The incoming request.
        rack (str): The rack which the lock resides on.
        board (str): The board which the lock resides on.
        device (str): The lock device.

    Returns:
        sanic.response.HTTPResponse: The endpoint response.
    """
    # FIXME - error out until a lock backend is actually implemented
    return errors.SynseError('Endpoint not yet implemented.')
    # await validate.validate_device_type(const.TYPE_LOCK, rack, board, device)
    #
    # qparams = validate.validate_query_params(
    #     request.raw_args,
    #     'action'
    # )
    #
    # param_action = qparams.get('action')
    #
    # # if a request parameter is specified, this will translate to a
    # # write request.
    # if param_action is not None:
    #     # validate the values of the action
    #     if param_action not in const.lock_actions:
    #         raise errors.InvalidArgumentsError(
    #             gettext('Invalid lock action "{}". Must be one of: {}').format(
    #                 param_action, const.lock_actions)
    #         )
    #
    #     data = {
    #         'action': param_action
    #     }
    #     transaction = await commands.write(rack, board, device, data)
    #     return transaction.to_json()
    #
    # # if no request parameter is specified, this will translate to a
    # # read request.
    # else:
    #     reading = await commands.read(rack, board, device)
    #     return reading.to_json()
