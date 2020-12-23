from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)
from setuptools import setup, find_packages

setup(
    name="kids_britannica",
    version=0.2,
    packages=find_packages(),
    install_requires=[
        "glob2",
        "jsonextended",
        "spacy",
        "gdown",
    ],
    author="Joseph Cappadona",
    author_email="josephcappadona27@gmail.com",
    description="a library to scrape and use data from kids.britannica.com",
    license="GPLv3",
)