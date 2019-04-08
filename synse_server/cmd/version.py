
import synse_server


def version():
    """Generate the version response data.

    Returns:
        dict: A dictionary representation of the version response.
    """
    return {
        'version': synse_server.__version__,
        'api_version': synse_server.__api_version__,
    }
