#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import io
import os

# Package meta-data
NAME = "paperless-ngx-n8n-mcp"
DESCRIPTION = "Model Context Protocol integration for Paperless-ngx and n8n"
URL = "https://github.com/PDangelmaier/paperless-ngx-n8n-integration"
EMAIL = "email@example.com"
AUTHOR = "PDangelmaier"
REQUIRES_PYTHON = ">=3.8.0"
VERSION = "0.1.0"

# What packages are required for this module to be executed?
with io.open("requirements.txt", encoding="utf-8") as f:
    REQUIRED = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Import the README and use it as the long-description.
with io.open("README.md", encoding="utf-8") as f:
    long_description = "\n" + f.read()

# Where the magic happens:
setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=("tests",)),
    install_requires=REQUIRED,
    include_package_data=True,
    license="MIT",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Networking",
    ],
    entry_points={
        "console_scripts": ["mcp-server=src.mcp_server:main"],
    },
    keywords=["paperless", "paperless-ngx", "n8n", "mcp", "model context protocol", "ai", "integration"],
    project_urls={
        "Bug Reports": f"{URL}/issues",
        "Source": URL,
    },
)

