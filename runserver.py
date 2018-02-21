"""Run Synse Server.
"""

from synse.factory import make_app


if __name__ == '__main__':
    app = make_app()
    app.run(
        host='0.0.0.0',
        port=5000,
    )
