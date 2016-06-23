#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

description = """
Encrypted PostgreSQL json field support for Django.
"""

setup(
    name="django-encrypted-pgjson",
    version="0.2.3",
    url="https://github.com/LucasRoesler/django-encrypted-json",
    license="MIT",
    platforms=["OS Independent"],
    description=description.strip(),
    author="Lucas Roesler",
    author_email="roesler.lucas@gmail.com",
    keywords="django, postgresql, pgsql, json, field, encryption",
    maintainer="Lucas Roesler",
    maintainer_email="roesler.lucas@gmail.com",
    packages=find_packages(),
    include_package_data=False,
    install_requires=[
        'cryptography',
        'django-pgjson'
    ],
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Topic :: Internet :: WWW/HTTP",
    ]
)
