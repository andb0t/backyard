#!/usr/bin/env python3
from setuptools import setup, find_packages


setup(
    name="backyard.module.arachni",
    version="1.0",
    author="Michael Lohr",
    author_email="michael@lohr-ffb.de",
    description="",

    packages=find_packages('src', exclude=['examples', 'tests']),
    package_dir={'': 'src'},
    namespace_packages=['backyard'],

    include_package_data=True,
    package_data={},

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
        'colorlog'
        ],

    entry_points="""
        [console_scripts]
        scanner-example = backyard.module.arachni.__main__:main
    """,
    )