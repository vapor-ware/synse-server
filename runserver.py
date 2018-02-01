"""Run Synse Server.
"""

from synse.factory import make_app
from synse import config


if __name__ == '__main__':

    config.load()

    app = make_app()

    app.run(
        host='0.0.0.0',
        port=5000,
    )