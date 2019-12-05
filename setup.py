#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Set up and install h5sh."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

setup_requirements = [
    "pytest-runner",
]

test_requirements = [
    "pytest",
]

setup(
    author="Seth Robert Johnson",
    author_email="johnsonsr@ornl.gov",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="Fast shell-like tool for interacting with HDF5 files.",
    entry_points={"console_scripts": ["h5sh=h5sh.scripts.main:main"],},
    include_package_data=True,
    install_requires=["h5py>=2.7.1", "prompt-toolkit>=2.0", "numpy>=1.15", "pygments"],
    license="BSD license",
    long_description=readme + "\n\n" + history,
    keywords="h5sh",
    name="h5sh",
    packages=find_packages(include=["h5sh"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/sethrj/h5sh",
    version="0.1.0",
    zip_safe=False,
)
