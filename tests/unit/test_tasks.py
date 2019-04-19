
from unittest import mock

from sanic import Sanic

from synse_server import tasks


def test_register_with_app():
    app = Sanic()
    app.add_task = mock.Mock()

    tasks.register_with_app(app)
    app.add_task.assert_called_once()
