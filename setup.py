# -*- coding: utf-8 -*-

from setuptools import setup

version = '0.9.1'
name = 'oasis'
short_description = 'A simple HTTP, PROXY, CGI, WSGI server'
with open("README.md") as f:
    long_description = f.read()

classifiers = [
   "Development Status :: 1 - Planning",
   "License :: OSI Approved :: MIT License",
   "Programming Language :: Python",
   "Topic :: Software Development",
]

setup(
    name=name,
    version=version,
    description=short_description,
    long_description=long_description,
    classifiers=classifiers,
    keywords=['oasis', 'wsgi', 'cgi', 'proxy', 'http', 'https'],
    author='Kenji Yano',
    author_email='kenji.yano@gmail.com',
    url='https://github.com/yanolab/oasis',
    license='MIT',
    packages=['oasis', 'oasis.wsgi'],
    test_suite='test.test.suite'
)
