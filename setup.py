#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='controller_ironcar_octonomous',
    version='1.0',
    packages=find_packages(exclude=["tests", "tests.*"]),
    license='MIT',
    long_description=open('README.md').read(),
    url='https://github.com/ironcarocto/controller_ironcar_octonomous',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Programming Language :: Python :: 3'
    ],
    entry_points={
        'console_scripts': [
            'controller_ironcar = controller_ironcar.simple_command:main',
        ],
    },
    install_requires=[
        'decorator',
        'h5py==2.7.0',
        'keras==1.2.0',
        'numpy',
        'Pillow',
        'socketIO-client==0.7.2'
    ],
    extras_require={
        'dev': [
            'pytest'
        ],
        'rasbperry': [
            'Adafruit_PCA9685',
            'picamera'
        ]
    }
)
