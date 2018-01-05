#!/usr/bin/env python
"""
This class contains data we save in the data file for all commits.
"""

import csv
import logging
import os

from data_file_line import DataFileLine  # pylint: disable=relative-import

logger = logging.getLogger(__name__)


class DataFile(object):
    """
    This class contains data we save in the data file for all commits.
    """
    def __init__(self, file_name, lines=None):
        """
        Create the data file.
        :param file_name: The name of the DataFile.
        :param lines: All lines in the data file (list).
        """
        self.file_name = file_name
        self.headers = [
            'hash',
            'author',
            'message',
            'status',
            'porter',
            'remote commit',
            'notes',
        ]
        if lines is None:
            self.lines = []
        else:
            self.lines = lines

    def append(self, line):
        """
        Append a line to a data file.
        :param line: The DataFileLine to append.
        """
        self.lines.append(line)

    def read(self):
        """
        Read in the data file.
        :return: A DataFile.
        """
        logger.debug('reading data file {}'.format(self.file_name))
        if not os.path.isfile(self.file_name):
            return self

        with open(self.file_name, 'rb') as f:
            reader = csv.reader(f)
            iter_reader = iter(reader)
            next(iter_reader)  # Skip headers.
            for row in iter_reader:
                logger.debug('reading row: {}'.format(row))
                line = DataFileLine(row[0], row[1], row[2], row[3], row[4], row[5], row[6])
                self.lines.append(line)
        return self

    def write(self):
        """
        Write out the data to the file.
        """
        logger.debug('writing data file {}'.format(self.file_name))
        with open(self.file_name, 'wb') as csvfile:
            w = csv.writer(csvfile)
            # Write headers.
            row = self.headers
            w.writerow(row)
            for line in self.lines:
                logger.debug('line as dict: {}'.format(line.__dict__))
                ld = line.__dict__
                row = list()
                row.append(ld['hash'])
                row.append(ld['author'])
                row.append(ld['message'])
                row.append(ld['status'])
                row.append(ld['porter'])
                row.append(ld['remote_commit'])
                row.append(ld['notes'])
                logger.debug('row : {}'.format(row))
                w.writerow(row)
