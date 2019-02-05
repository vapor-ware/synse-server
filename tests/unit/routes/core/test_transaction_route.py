"""Test the 'synse_server.routes.core' Synse Server module's transaction route."""

import asynctest
import pytest
from sanic.response import HTTPResponse

import synse_server.commands
from synse_server.routes.core import transaction_route
from synse_server.scheme.base_response import SynseResponse
from tests import utils


def mockreturn(transaction):
    """Mock method that will be used in monkeypatching the command."""
    r = SynseResponse()
    r.data = {'id': transaction}
    return r


@pytest.fixture()
def mock_transaction(monkeypatch):
    """Fixture to monkeypatch the underlying Synse command."""
    mock = asynctest.CoroutineMock(synse_server.commands.check_transaction, side_effect=mockreturn)
    monkeypatch.setattr(synse_server.commands, 'check_transaction', mock)
    return mock_transaction


@pytest.mark.asyncio
async def test_synse_transaction_route(mock_transaction, no_pretty_json):
    """Test a successful transaction check."""

    cases = [
        '123456',
        'abcdef',
        '!@#$%^',
        ''
    ]

    for case in cases:

        result = await transaction_route(utils.make_request('/synse/transaction'), case)
        expected = '{{"id":"{0}"}}'.format(case)

        assert isinstance(result, HTTPResponse)
        assert result.body == expected.encode('ascii')
        assert result.status == 200
