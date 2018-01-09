#!/usr/bin/env python
"""
This class contains data we save in the data file for each commit. This
represents one line of the data file.
"""

import logging

logger = logging.getLogger(__name__)


class DataFileLine(object):
    """
    This class contains data we save in the data file for each commit. This
    represents one line of the data file.
    """

    def __init__(
            self, _hash, author, message,
            status='open', porter=None, remote_commit=None, notes=None):
        """
        Create a DataFileLine.
        :param _hash: The commit hash from the local repo.
        :param author: The author of the commit in the local repo.
        :param message: The commit message from the local repo.
        :param status: The status of the commit in the remote repo.
        (open/unnecessary/completed)
        :param porter: The user who ported this commit or deemed it unnecessary
        to port.
        :param remote_commit: The corresponding commit in the other repo. For
        example if this data file is for synse-server-internal the
        remote_commit would be the corresponding commit in synse-server.
        :param notes: Optional notes.
        """
        self.hash = _hash
        self.author = author
        self.message = message
        self.status = status
        self.porter = porter
        self.remote_commit = remote_commit
        self.notes = notes

    def update_notes(self, notes):
        """
        Update the notes field in DataFileLine line.
        :param notes: The data to update notes to.
        """
        if notes is not None:
            if self.notes:
                if self.notes != notes:
                    logger.warn('Overwriting exiting notes [{}] with [{}].'.format(
                        self.notes, notes))
            self.notes = notes

    def update_porter(self, porter):
        """
        Update the porter field in DataFileLine line.
        :param porter: The data to update porter to.
        """
        if self.porter:
            if self.porter != porter:
                logger.warn('Overwriting exiting porter {} with {}.'.format(
                    self.porter, porter))
        self.porter = porter

    def update_remote_commit(self, remote_commit):
        """
        Update the status field in DataFileLine line.
        :param remote_commit: The data to update remote_commit to.
        """
        if remote_commit is not None:
            if self.remote_commit:
                if self.remote_commit != remote_commit:
                    logger.warn('Overwriting exiting remote commit {} with {}.'.format(
                        self.remote_commit, remote_commit))
            self.remote_commit = remote_commit

    def update_status(self, status):
        """
        Update the status field in DataFileLine line.
        :param status: The data to update status to.
        """
        if status is not None:
            if status in ['o', 'open']:
                status = 'open'
            elif status in ['u', 'unnecessary']:
                status = 'unnecessary'
            elif status in ['c', 'completed']:
                status = 'completed'
            else:
                raise ValueError('Unknown status: {}'.format(status))

            if self.status is not None and self.status != 'open':
                if self.status != status:
                    logger.warn('Overwriting exiting status {} with {}.'.format(
                        self.status, status))
            self.status = status
