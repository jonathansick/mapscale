#!/usr/bin/env python
# encoding: utf-8
"""
mapscale: Embarassingly parallel processing with ZeroMQ

Copyright 2012 Jonathan Sick
"""
import os
from setuptools import setup
from sphinx.setup_command import BuildDoc


def read(fname):
    """Courtesy of:
    http://packages.python.org/an_example_pypi_project/setuptools.html
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

cmdclass = {'docs': BuildDoc}

setup(
    name="MapScale",
    version="0.1.0",
    author="Jonathan Sick",
    author_email="jonathansick@mac.com",
    description="ZeroMQ-based replacement for multiprocessing's Pool.map()",
    long_description=read("README.markdown"),
    url="http://www.jonathansick.ca",
    packages=["mapscale"],
    cmdclass=cmdclass,
    classifiers=["Development Status :: 3 - Alpha"]
)
