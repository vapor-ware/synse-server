#!/usr/bin/env python
"""
"""

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
    package_data={
        'synse.emulator': [
            'config/proto/*.yml',
            'config/sensor/*.yml'
        ]
    },
    zip_safe=False
)
