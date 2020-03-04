"""Retry backoff strategies."""

import random
import time
from typing import Union

__all__ = ['ExponentialBackoff']


class ExponentialBackoff:
    """An implementation of the exponential backoff strategy.

    This is useful for getting an exponentially backed-off delay for
    reconnection or retry actions.

    Each call to ``delay`` will return the next exponentially backed-off
    value, in seconds, to use for waiting. The backoff will continue for
    each call, up to a maximum of 2^10 * base.

    Args:
        base: The base delay, in seconds. This is the starting point for
            the returned exponentially backed off time values.
        cap: The cap on the exponent, after which the backoff will not
            grow exponentially. This is 9 by default (2^9 = 512 ~= 8.5 minutes)
    """

    def __init__(self, base: int = 1, cap: int = 9) -> None:
        self._base = base
        self._exp = 0
        self._max = cap

        self._reset_time = base * 2 ** (self._max + 1)
        self._last_invocation = time.monotonic()

        self.rand = random.Random()
        self.rand.seed()

    def delay(self) -> Union[int, float]:
        """Get the next exponentially backed off time delay, in seconds.

        The delay value is incremented exponentially with every call, up
        to the defined max. If a period of time greater than 2^(max+1) * base
        has passed, the backoff is reset.

        Returns:
            The time, in seconds, to be used as the next delay interval.
        """
        invocation = time.monotonic()
        interval = invocation - self._last_invocation
        self._last_invocation = invocation

        if interval > self._reset_time:
            self._exp = 0

        self._exp = min(self._exp + 1, self._max)
        return self.rand.uniform(0, self._base * 2 ** self._exp)
