#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='controller_ironcar_octonomous',
    version='1.0',
    packages=find_packages(exclude=["*_tests"]),
    license='',
    long_description=open('README.md').read(),
    classifier= [
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3'
    ],
    entry_points = {
        'console_scripts': [
            'indexer = python.simple_command:main',
        ],
    },
    install_requires = [
        'numpy',
        'Adafruit_PCA9685',
        'Adafruit_BNO055',
        'picamera',
        'keras==1.2.0',
        'h5py==2.7.0',
        'socketIO-client==0.7.2'
    ],
    extras_require={
        'dev': [
            'inputs'
        ]
    }
)