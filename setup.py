from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

from setuptools import setup, find_packages

setup(
    name="kids_britannica",
    version=0.1,
    packages=find_packages(exclude=("utils",)),
    install_requires=[
        "requests",
        "wget",
        "glob2",
        "numpy",
        "beautifulsoup4",
        "dataclasses",
        "m3u8downloader"
    ],
    dependency_links=[
        "https://github.com/josephcappadona/m3u8downloader.git#egg=m3u8downloader"
    ],
    author="Joseph Cappadona",
    author_email="josephcappadona27@gmail.com",
    description="a library to scrape and use data from kids.britannica.com",
    license="GPLv3",
)