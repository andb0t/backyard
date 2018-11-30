#!/usr/bin/env python3
import os
from setuptools import setup, find_packages


data_files = []
for path, dirs, files in os.walk("src/backyard/supervisor/config"):
    for f in files:
        data_files.append(os.path.join(path[17:], f))

setup(
    name="backyard.api",
    version="1.0",
    author="GONICUS GmbH",
    author_email="info@gonicus.de",
    description="",

    packages=find_packages('src', exclude=['examples', 'tests']),
    package_dir={'': 'src'},
    namespace_packages=['backyard'],

    include_package_data=True,
    package_data={
        'backyard.supervisor': data_files
        },

    zip_safe=False,

    setup_requires=[
        'pylint',
        ],
    tests_require=[
        'pytest',
        ],
    install_requires=[
        'protobuf',
        'asyncio-nats-client',
        'connexion',
        'connexion[swagger-ui]',
        'python_dateutil',
        'aiohttp',
        'aiohttp_jinja2',
        'pyyaml',
        'motor',
        'colorlog'
        ],

    entry_points="""
        [console_scripts]
        backyard-api = backyard.api.__main__:main
        backyard-supervisor = backyard.supervisor.__main__:main
    """,
    )
