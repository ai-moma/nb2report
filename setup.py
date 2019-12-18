#!/usr/bin/env python
# -*- coding: utf-8 -*-
import setuptools

from pip._internal.download import PipSession
from pip._internal.req import parse_requirements

from os import path

here = path.abspath(path.dirname(__file__))

with open("README.md", "r") as fh:
    long_description = fh.read()

requirements = [str(ir.req) for ir in parse_requirements('requirements.txt', session=PipSession())]

test_requirements = [str(ir.req) for ir in parse_requirements('requirements_test.txt', session=PipSession())]

setuptools.setup(
    name="nb2report",
    version="0.0.4",
    author="Boris Fajardo",
    author_email="bfajardo@datiobd.com",
    description="Convert a markdown jupyter notebook into an html report.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ai-moma/nb2report",
    packages=setuptools.find_packages(exclude=("tests",)),
    package_data={'nb2report': ['.config/*']},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={'console_scripts': ["nb2report=nb2report.cli:cli"]},
    install_requires=['Click']
)
