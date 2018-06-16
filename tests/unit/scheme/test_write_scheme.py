"""Test the 'synse.scheme.write' Synse Server module."""

from synse_grpc import api

from synse.scheme.write import WriteResponse


def test_write_scheme():
    """Check that the write scheme matches the expected."""

    wd1 = api.WriteData(data=b'test', action='test1')
    wd2 = api.WriteData(data=b'test', action='test2')
    wd3 = api.WriteData(data=b'test', action='test3')

    transactions = {
        '123456': wd1,
        'abcdef': wd2,
        '!@#$%^': wd3
    }

    response_scheme = WriteResponse(transactions)

    assert response_scheme.data == [
        {
            'context': {
                'action': wd1.action,
                'data': wd1.data
            },
            'transaction': '123456'
        },
        {
            'context': {
                'action': wd2.action,
                'data': wd2.data
            },
            'transaction': 'abcdef'
        },
        {
            'context': {
                'action': wd3.action,
                'data': wd3.data
            },
            'transaction': '!@#$%^'
        }
    ]
