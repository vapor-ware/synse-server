#!/usr/bin/env python
"""
This class contains data we get from the git commit log for each commit.
"""

import logging

logger = logging.getLogger(__name__)


class CommitData(object):
    """
    This class contains data we get from the git commit log for each commit.
    """

    def __init__(self, _hash, author, message):
        """
        Initialize CommitData
        :param _hash: Short git hash.
        :param author: Git author.
        :param message: The git commit message.
        """
        self.hash = _hash
        self.author = author
        self.message = message
        logger.debug('hash: {}'.format(self.hash))
        logger.debug('author: {}'.format(self.author))
        logger.debug('message: {}'.format(self.message))
