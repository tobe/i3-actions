#!/usr/bin/env python3
# -*- coding: utf-8 -*-!

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

import i3actions

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='i3-actions',
    version=i3actions.__version__,
    description='i3-actions is a python3 utility for i3-wm which mostly makes window managment simpler and faster by integrating with dmenu.',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/infyhr/i3-actions',

    # Scriptzz
    scripts = ['i3actions.py'],

    # Author details
    author='T.B. (infyhr)',
    author_email='infy@cybershade.org',

    # Choose your license
    license='MIT',

    # Requirements
    install_requires=['i3ipc'],
)

