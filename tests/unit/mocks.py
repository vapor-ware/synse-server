"""Mock object implementations to be used in unit testing."""


class OptionsMock:
    """OptionsMock can be used to mock the ``synse_server.config.options`` object.

    While the real object is of type ``bison.Bison``, the access patterns for
    the object are generally through a ``.get()`` method. Keys added to the mock
    will need to be added with their full dot prefix if the lookup key is a
    dot-compound key.
    """

    def __init__(self, values):
        self.values = values

    def get(self, key, default=None):
        """Get the value for the key."""
        return self.values.get(key, default)
