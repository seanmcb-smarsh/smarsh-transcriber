__copyright__ = "Copyright (C) 2021, Smarsh, All rights reserved"

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup
from setuptools import find_packages

setup(
    name="transcriber-api",
    python_requires=">=3.6",
    version="0.0.0",
    author="Smarsh Inc",
    author_email="support@smarsh.com",
    url="https://www.smarsh.com",
    description="API for transcription",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)