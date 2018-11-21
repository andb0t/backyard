#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name = "backyard.analyzer.example",
    version = "1.0",
    author = "GONICUS GmbH",
    author_email = "info@gonicus.de",
    description = "",

    packages = find_packages('src', exclude=['examples', 'tests']),
    package_dir={'': 'src'},
    namespace_packages = ['backyard'],

    include_package_data = True,
    package_data = {},

    zip_safe = False,

    setup_requires = [
        'pylint',
        ],
    tests_require = [
        'pytest',
    ],
    install_requires = [
        'protobuf',
        'asyncio-nats-client',
        'colorlog'
        ],

    entry_points = """
        [console_scripts]
        analyzer-example = backyard.analyzer.example.__main__:main
    """,
)
