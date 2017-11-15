"""Test the 'synse.scheme.write' Synse Server module.
"""

from synse_plugin import api

from synse.scheme.write import WriteResponse


def test_write_scheme():
    """Check that the write scheme matches the expected.
    """
    wd1 = api.WriteData(raw=[b'test'], action='test1')
    wd2 = api.WriteData(raw=[b'test'], action='test2')
    wd3 = api.WriteData(raw=[b'test'], action='test3')

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
                'raw': wd1.raw
            },
            'transaction': '123456'
        },
        {
            'context': {
                'action': wd2.action,
                'raw': wd2.raw
            },
            'transaction': 'abcdef'
        },
        {
            'context': {
                'action': wd3.action,
                'raw': wd3.raw
            },
            'transaction': '!@#$%^'
        }
    ]
