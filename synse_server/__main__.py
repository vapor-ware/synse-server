"""Entry point script for Synse Server.

This entry point script runs when the 'synse_server' module is called directly.
Synse Server is initialized and run via this entry point in its Docker image.

The application is configured to listen on host 0.0.0.0, port 5000.

Example Usage:

    $ python synse_server
"""

from synse_server.server import Synse

# Initialize a new instance of Synse Server.
server = Synse(
    host='0.0.0.0',
    port=5000,
)

server.run()
