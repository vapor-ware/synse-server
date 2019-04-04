#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup and packaging for Synse Server."""

import os

from setuptools import find_packages, setup


here = os.path.abspath(os.path.dirname(__file__))

# Load the package's __init__.py file as a dictionary.
pkg = {}
with open(os.path.join(here, 'synse_server', '__init__.py')) as f:
    exec(f.read(), pkg)

# Load the README
readme = ""
if os.path.exists('README.md'):
    with open('README.md', 'r') as f:
        readme = f.read()

setup(
    name=pkg['__title__'],
    version=pkg['__version__'],
    description=pkg['__description__'],
    url=pkg['__url__'],
    author=pkg['__author__'],
    author_email=pkg['__author_email__'],
    license=pkg['__license__'],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['LICENSE'],
        'synse_server': ['locale/*/LC_MESSAGES/*.mo'],
    },
    scripts=['bin/synse-server'],
    python_requires='>=3.6',
    install_requires=[
        'aiocache',
        'bison>=0.1.0',
        'grpcio',
        'kubernetes',
        'python-json-logger',
        'pyyaml>=4.2b1',
        'requests>=2.20.0',  # used by 'kubernetes'
        'sanic>=0.8.0',
        'structlog',
        'synse-grpc>=1.1.0',  # fixme: this will need to be >= 3.0.0 once that is released
    ],
    tests_require=[
        'aiohttp',
        'asynctest',
        'pytest',
        'pytest-asyncio',
        'pytest-mock'
    ],
    zip_safe=False,
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ]
)
