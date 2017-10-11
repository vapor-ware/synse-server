"""

"""

from synse.factory import make_app
from synse import config


if __name__ == '__main__':

    config.load()

    app = make_app()
    app.register_background_processes()

    app.run(
        host=config.options.get('host'),
        port=config.options.get('port'),
        log_config=config.LOGGING
    )
