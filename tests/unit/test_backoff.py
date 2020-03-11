"""Unit tests for the ``synse_server.backoff`` module."""

from synse_server import backoff


class TestExponentialBackoff:

    def test_delay(self):
        back = backoff.ExponentialBackoff()

        delay_1 = back.delay()
        delay_2 = back.delay()
        delay_3 = back.delay()
        delay_4 = back.delay()
        delay_5 = back.delay()
        delay_6 = back.delay()
        delay_7 = back.delay()
        delay_8 = back.delay()
        delay_9 = back.delay()
        delay_10 = back.delay()
        delay_11 = back.delay()
        delay_12 = back.delay()

        assert 0 < delay_1 < 2
        assert 0 < delay_2 < 4
        assert 0 < delay_3 < 8
        assert 0 < delay_4 < 16
        assert 0 < delay_5 < 32
        assert 0 < delay_6 < 64
        assert 0 < delay_7 < 128
        assert 0 < delay_8 < 256
        assert 0 < delay_9 < 512  # hit the max, should not exceed
        assert 0 < delay_10 < 512
        assert 0 < delay_11 < 512
        assert 0 < delay_12 < 512
