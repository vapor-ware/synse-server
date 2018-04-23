"""Entry point for Synse Server.

This entry point script will run when the Synse Server
module is called directly. It starts up a default
configuration of Synse Server listening on host '0.0.0.0'
and port 5000.

Example Usage:

    $ python synse
"""

from synse.factory import make_app


app = make_app()
app.run(
    host='0.0.0.0',
    port=5000,
)
