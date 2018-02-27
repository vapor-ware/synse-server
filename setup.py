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
    license='GPL v2.0',
    packages=find_packages(),
    zip_safe=False
)
