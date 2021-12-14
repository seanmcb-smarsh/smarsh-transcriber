__copyright__ = "Copyright (C) 2021, Smarsh, All rights reserved"

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from package import Package
from setuptools import setup
from setuptools import find_packages
from version import __version__

setup(
    name="transcriber-api",
    python_requires="=3.6",
    version=__version__,
    author="Smarsh Inc",
    author_email="support@smarsh.com",
    url="https://www.smarsh.com",
    description="API for transcription",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    cmdclass={
        "package": Package
    },
)