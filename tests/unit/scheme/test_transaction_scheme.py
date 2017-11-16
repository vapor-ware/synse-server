"""Test the 'synse.scheme.transaction' Synse Server module."""

from synse_plugin import api

from synse.scheme.transaction import TransactionResponse


def test_transaction_scheme():
    """Test that the transaction scheme matches the expected."""

    tid = '123456'
    ctx = {
        'action': 'test',
        'raw': ['abcd']
    }
    wr = api.WriteResponse(
        created='october',
        updated='november',
        status=3,
        state=0,
    )

    response_scheme = TransactionResponse(tid, ctx, wr)

    assert response_scheme.data == {
        'id': tid,
        'context': ctx,
        'state': 'ok',
        'status': 'done',
        'created': 'october',
        'updated': 'november',
        'message': ''
    }
