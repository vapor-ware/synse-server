#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Setup and packaging for Synse Server."""

import os

from babel.messages import frontend as babel
from setuptools import find_packages, setup


here = os.path.abspath(os.path.dirname(__file__))

# Load the package's __init__.py file as a dictionary.
pkg = {}
with open(os.path.join(here, 'synse', '__init__.py')) as f:
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
    package_data={'': ['LICENSE']},
    python_requires='==3.6',
    install_requires=[
        'aiocache',
        'grpcio',
        'pyyaml',
        'sanic',
        'synse-plugin',
        'bison>=0.0.5'
    ],
    zip_safe=False,
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    cmdclass={
        'compile_catalog': babel.compile_catalog,
        'extract_messages': babel.extract_messages,
        'init_catalog': babel.init_catalog,
    }
)
