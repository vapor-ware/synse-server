#!/usr/bin/env python
"""Setup and packaging for Synse Server."""

from setuptools import setup, find_packages

import synse


setup(
    name=synse.__title__,
    version=synse.__version__,
    description=synse.__description__,
    url=synse.__url__,
    author=synse.__author__,
    author_email=synse.__author_email__,
    license='GNU General Public License v2.0',
    python_requires='==3.6',
    packages=find_packages(),
    zip_safe=False
)
