"""Test the 'synse.routes.core' Synse Server module's transaction route.
"""
# pylint: disable=redefined-outer-name,unused-argument

import asynctest
import pytest
from sanic.response import HTTPResponse

import synse.commands
from synse import config
from synse.routes.core import transaction_route
from synse.scheme.base_response import SynseResponse


def mockreturn(transaction):
    """Mock method that will be used in monkeypatching the command."""
    r = SynseResponse()
    r.data = {'id': transaction}
    return r


@pytest.fixture()
def mock_transaction(monkeypatch):
    """Fixture to monkeypatch the underlying Synse command."""
    mock = asynctest.CoroutineMock(synse.commands.check_transaction, side_effect=mockreturn)
    monkeypatch.setattr(synse.commands, 'check_transaction', mock)
    return mock_transaction


@pytest.fixture()
def no_pretty_json():
    """Fixture to ensure basic JSON responses."""
    config.options['pretty_json'] = False


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

        result = await transaction_route(None, case)
        expected = '{{"id":"{0}"}}'.format(case)

        assert isinstance(result, HTTPResponse)
        assert result.body == expected.encode('ascii')
        assert result.status == 200
