"""Test the 'synse_server.scheme.transaction' Synse Server module."""

from synse_grpc import api

from synse_server.scheme.transaction import (TransactionListResponse,
                                             TransactionResponse)


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


def test_transaction_list_scheme():
    """Test that the transaction list scheme matches the expected.

    Here, the TransactionListResponse just sets the data its given
    (a list of string) to its `data` field, so we just check that
    the data field is set.
    """
    ids = [
        'abcdefg',
        'hijklmn',
        'opqrstu',
        'vwxyz',
        '12345'
    ]

    response_scheme = TransactionListResponse(ids)
    assert response_scheme.data == ids
