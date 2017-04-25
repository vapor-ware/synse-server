#!/usr/bin/env python
""" Developer script used to correct the numbering of test cases in a
Python test file.

This script expects that the test methods are defined as:

  def test_*

If the tests are not named in that manner, they will not be included in
the test numbering rewrites.

This script takes 1..N arguments which can be either a file or a directory
of test files to update. If a directory is specified, all python files whose
name begins with 'test_' will be included in the numbering rewrite.

The file will be replaced with the newly numbered file.

    Author: Erick Daniszewski
    Date:   08/15/2016

    \\//
     \/apor IO
"""
import sys
import os
from itertools import count

paths = sys.argv[1:]


def process_file(filename, counter):
    with open(filename, 'r') as f:
        data = f.readlines()

    for i in xrange(len(data)):
        line = data[i]
        if 'def test_' in line:
            components = line.split('_')
            for j in xrange(len(components)):
                comp = components[j]
                if comp.isdigit():
                    components[j] = str(counter.next()).zfill(3)
                    break
            data[i] = '_'.join(components)

    with open(filename, 'w+') as f:
        f.writelines(data)

for path in paths:
    if os.path.isdir(path):
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isfile(full_path) and item.startswith('test_') and item.endswith('.py'):
                process_file(full_path, count())

    elif os.path.isfile(path):
        p, n = os.path.split(path)
        if n.startswith('test_'):
            process_file(path, count())
