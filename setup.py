#!/usr/bin/env python
# encoding: utf-8
"""
mapscale: Embarassingly parraling processing with ZeroMQ

Copyright 2012 Jonathan Sick
"""
import os
from setuptools import setup


def read(fname):
    """Courtesy of:
    http://packages.python.org/an_example_pypi_project/setuptools.html
    """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="MapScale",
    version="0.0.1",
    author="Jonathan Sick",
    author_email="jonathansick@mac.com",
    description="ZeroMQ-based replacement for multiprocessing's Pool.map()",
    long_description=read("README.markdown"),
    url="http://www.jonathansick.ca",
    packages=["mapscale"],
    classifiers=["Development Status :: 2 - Pre-Alpha"]
)
