#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'tardis'

from locust import HttpLocust
from testes import CONF


class MainTest(HttpLocust):
    host = CONF.host
