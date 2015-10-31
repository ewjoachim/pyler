# -*- coding: utf-8 -*-

# Copyright (c) 2015 Joachim Jablon

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Python Future imports
from __future__ import unicode_literals

# Python System imports

# Third-party imports
from setuptools import setup, find_packages

# Relative imports

# Technicals parameters you need to set
NAME = "pyler"

DESCRIPTION = "Helper architecture for tackling Project Euler problems"

WEBSITE = "https://github.com/ewjoachim/pyler"

# Technical parameters that should be more or less the same for every projects
CLASSIFIERS = [
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.4',
]

AUTHORS = [
    ("Joachim Jablon", "ewjoachim@gmail.com"),
]

REQUIREMENTS = [
    "beautifulsoup4",
    "requests",
]

setup(
    name=NAME,
    version="0.0.1",
    author=", ".join([author[0] for author in AUTHORS]),
    author_email=", ".join([author[1] for author in AUTHORS]),
    url=WEBSITE,
    packages=find_packages(),
    description=DESCRIPTION,
    include_package_data=True,
    classifiers=CLASSIFIERS,
    install_requires=REQUIREMENTS,
    entry_points={
        'console_scripts': ['pyler=pyler.__main__:main'],
    },
)
