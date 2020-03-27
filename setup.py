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
    long_description=readme,
    long_description_content_type='text/markdown',
    url=pkg['__url__'],
    author=pkg['__author__'],
    author_email=pkg['__author_email__'],
    license=pkg['__license__'],
    packages=find_packages(exclude=['tests.*', 'tests']),
    include_package_data=True,
    python_requires='>=3.6',
    package_data={
        '': ['LICENSE'],
    },
    entry_points={
        'console_scripts': [
            'synse_server = synse_server.__main__:main',
        ],
    },
    install_requires=[
        'aiocache',
        'bison>=0.1.0',
        'grpcio',
        'kubernetes',
        'pyyaml>=4.2b1',
        'sanic>=0.8.0',
        'prometheus-client',
        'shortuuid',
        'structlog>=20.1.0',
        'websockets',
        'synse-grpc==3.0.0',
    ],
    zip_safe=False,
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ]
)
