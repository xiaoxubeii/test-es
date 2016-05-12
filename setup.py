#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'tardis'

import setuptools

setuptools.setup(
    name='testes',
    version='0.2.0',
    packages=setuptools.find_packages(),
    package_data={'testes': ['*.csv', 'templates/*', 'test_data/*']})
